import json
import pathlib
from typing import ClassVar

import jsonschema
import pytest
from jsonschema.exceptions import ValidationError

JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


@pytest.fixture(scope="session")
def schema():
    path = pathlib.Path(__file__).parent.parent / "schema.json"
    return json.loads(path.read_text())


def embed_attributes(**attrs: JSON) -> JSON:
    return {"zarr_format": 3, "node_type": "group", "attributes": attrs}


convention_metadata = {
    "schema_url": "https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v1/schema.json",
    "spec_url": "https://github.com/zarr-conventions/dggs/blob/v1/README.md",
    "uuid": "7b255807-140c-42ca-97f6-7a1cfecdbc38",
    "name": "dggs",
    "description": "Discrete Global Grid Systems convention for zarr",
}


def test_schema(schema):
    validator = jsonschema.validators.validator_for(schema)
    validator.check_schema(schema)


def test_validate_missing_convention_declaration(schema):
    data: JSON = embed_attributes(
        dggs={
            "name": "h3",
            "refinement_level": 10,
            "spatial_dimension": "cell",
            "coordinate": "cell_ids",
            "compression": "none",
        }
    )

    with pytest.raises(ValidationError):
        jsonschema.validate(data, schema)


class TestCompression:
    dggs: ClassVar[JSON] = {
        "name": "healpix",
        "refinement_level": 10,
        "indexing_scheme": "nested",
        "spatial_dimension": "cells",
    }

    @pytest.mark.parametrize(
        ["name", "level", "scheme", "compression"],
        [
            ("healpix", 10, "nested", "none"),
            ("healpix", None, "zuniq", "none"),
            ("healpix", None, "zuniq", "compacted"),
            ("healpix", 29, "nested", "ranges"),
            ("h3", None, None, "none"),
            ("h3", 10, None, "compacted"),
            ("h3", 10, None, "ranges"),
        ],
    )
    def test_compression_valid(self, schema, name, level, scheme, compression):
        dggs: JSON = {
            "name": name,
            "refinement_level": level,
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": compression,
        }
        if scheme is not None:
            dggs["indexing_scheme"] = scheme
        data: JSON = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)

        jsonschema.validate(data, schema)

    @pytest.mark.parametrize("compression", ["unknown", "invalid"])
    def test_compression_invalid(self, schema, compression):
        additional_metadata: JSON = {
            "coordinate": "cell_ids",
            "compression": compression,
        }
        data: JSON = embed_attributes(
            zarr_conventions=[convention_metadata], dggs=self.dggs | additional_metadata
        )

        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)

    @pytest.mark.parametrize("compression", ["none", "compacted", "ranges"])
    def test_compression_coordinate_missing(self, schema, compression):
        additional_metadata: JSON = {"compression": compression}
        data = embed_attributes(
            zarr_conventions=[convention_metadata], dggs=self.dggs | additional_metadata
        )
        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)

    def test_coordinate_compression_missing(self, schema):
        additional_metadata: JSON = {"coordinate": "cell_ids"}
        data = embed_attributes(
            zarr_conventions=[convention_metadata], dggs=self.dggs | additional_metadata
        )
        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)

    def test_null_level_coordinate_missing(self, schema):
        dggs = {"name": "h3", "refinement_level": None, "spatial_dimension": "cells"}
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)

    @pytest.mark.parametrize("compression", ["compacted", "ranges"])
    def test_null_level_compressed(self, schema, compression):
        dggs = {
            "name": "h3",
            "refinement_level": None,
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": compression,
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)

    @pytest.mark.parametrize(
        ["level", "scheme", "compression"],
        [
            (10, "nested", "compacted"),
            (10, "zuniq", "compacted"),
            (None, "nuniq", "compacted"),
            (10, "nested", "ranges"),
            (29, "ring", "ranges"),
            (None, "zuniq", "ranges"),
        ],
    )
    def test_healpix_compression_table(self, schema, level, scheme, compression):
        dggs = {
            "name": "healpix",
            "refinement_level": level,
            "indexing_scheme": scheme,
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": compression,
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)


def test_name_not_lower_case(schema):
    dggs = {"name": "HEALPix", "refinement_level": 4, "spatial_dimension": "cells"}
    data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
    with pytest.raises(ValidationError):
        jsonschema.validate(data, schema)


def test_additional_parameters(schema):
    dggs = {
        "name": "generic",
        "refinement_level": 4,
        "generic_parameter": "some_value",
        "spatial_dimension": "cells",
    }
    data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)

    jsonschema.validate(data, schema)


class TestHealpix:
    def test_additional_parameters(self, schema):
        dggs = {
            "name": "healpix",
            "refinement_level": 4,
            "indexing_scheme": "nested",
            "generic_parameter": "some_value",
            "spatial_dimension": "cells",
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)

        jsonschema.validate(data, schema)

    def test_indexing_scheme_missing(self, schema):
        dggs = {
            "name": "healpix",
            "refinement_level": 10,
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": "none",
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)

    @pytest.mark.parametrize("scheme", ["nested", "ring"])
    def test_constant_scheme(self, schema, scheme):
        dggs = {
            "name": "healpix",
            "refinement_level": 10,
            "indexing_scheme": scheme,
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": "none",
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
        jsonschema.validate(data, schema)

    def test_variable_scheme(self, schema):
        dggs = {
            "name": "healpix",
            "refinement_level": None,
            "indexing_scheme": "zuniq",
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": "none",
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
        jsonschema.validate(data, schema)

    def test_indexing_scheme_invalid(self, schema):
        # indexing schemes that don't have a suffix of `uniq` are allowed without restrictions
        dggs = {
            "name": "healpix",
            "refinement_level": 10,
            "indexing_scheme": "unknown_scheme",
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": "none",
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
        jsonschema.validate(data, schema)

    def test_zuniq_concrete_level(self, schema):
        dggs = {
            "name": "healpix",
            "refinement_level": 10,
            "indexing_scheme": "zuniq",
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": "none",
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)

        jsonschema.validate(data, schema)


class TestEllipsoid:
    dggs_metadata: ClassVar[JSON] = {
        "name": "h3",
        "refinement_level": 10,
        "spatial_dimension": "cell",
        "coordinate": "cell_ids",
        "compression": "none",
    }

    def test_validate_implicit_sphere(self, schema):
        data: JSON = embed_attributes(
            zarr_conventions=[convention_metadata], dggs=self.dggs_metadata
        )
        jsonschema.validate(data, schema)

    def test_validate_semi_minor_axis(self, schema):
        ellipsoid = {
            "name": "WGS84",
            "semi_major_axis": 6378137.0,
            "semi_minor_axis": 6356752.314,
        }
        data = embed_attributes(
            zarr_conventions=[convention_metadata],
            dggs=self.dggs_metadata | {"ellipsoid": ellipsoid},
        )
        jsonschema.validate(data, schema)

    def test_validate_inverse_flattening(self, schema):
        ellipsoid = {
            "name": "WGS84",
            "semi_major_axis": 6378137.0,
            "inverse_flattening": 298.257223563,
        }
        data = embed_attributes(
            zarr_conventions=[convention_metadata],
            dggs=self.dggs_metadata | {"ellipsoid": ellipsoid},
        )
        jsonschema.validate(data, schema)

    def test_validate_explicit_sphere(self, schema):
        ellipsoid = {"name": "sphere", "radius": 6370997.0}

        data = embed_attributes(
            zarr_conventions=[convention_metadata],
            dggs=self.dggs_metadata | {"ellipsoid": ellipsoid},
        )
        jsonschema.validate(data, schema)

    @pytest.mark.parametrize(
        "fields",
        [
            ["radius", "semi_major_axis"],
            ["radius", "semi_minor_axis"],
            ["radius", "inverse_flattening"],
            ["radius", "semi_major_axis", "semi_minor_axis"],
            ["radius", "semi_major_axis", "inverse_flattening"],
            ["semi_major_axis", "semi_minor_axis", "inverse_flattening"],
            ["radius", "semi_major_axis", "semi_minor_axis", "inverse_flattening"],
        ],
    )
    def test_validate_mixed_fields(self, schema, fields):
        values = {
            "radius": 6370997.0,
            "semi_major_axis": 6378137.0,
            "semi_minor_axis": 6356752.314,
            "inverse_flattening": 298.257223563,
        }
        ellipsoid = {"name": "mixed"} | {field: values[field] for field in fields}
        data = embed_attributes(
            zarr_conventions=[convention_metadata],
            dggs=self.dggs_metadata | {"ellipsoid": ellipsoid},
        )

        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)

    def test_name_missing(self, schema):
        ellipsoid = {"radius": 6370997.0}
        data = embed_attributes(
            zarr_conventions=[convention_metadata],
            dggs=self.dggs_metadata | {"ellipsoid": ellipsoid},
        )

        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)
