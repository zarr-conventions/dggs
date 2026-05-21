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

    @pytest.mark.parametrize("compression", ["none", "compacted", "ranges"])
    def test_compression_valid(self, schema, compression):
        additional_metadata: JSON = {
            "coordinate": "cell_ids",
            "compression": compression,
        }
        data: JSON = embed_attributes(
            zarr_conventions=[convention_metadata], dggs=self.dggs | additional_metadata
        )

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

    def test_compression_coordinate_missing_valid(self, schema):
        additional_metadata: JSON = {"compression": "none"}
        data: JSON = embed_attributes(
            zarr_conventions=[convention_metadata], dggs=self.dggs | additional_metadata
        )
        jsonschema.validate(data, schema)

    @pytest.mark.skip(reason="not yet encoded in the schema")
    @pytest.mark.parametrize("compression", ["compacted", "ranges"])
    def test_compression_coordinate_missing_invalid(self, schema, compression):
        additional_metadata: JSON = {"compression": compression}
        data = embed_attributes(
            zarr_conventions=[convention_metadata], dggs=self.dggs | additional_metadata
        )
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
        dggs = {
            "name": "healpix",
            "refinement_level": 10,
            "indexing_scheme": "invalid",
            "spatial_dimension": "cells",
            "coordinate": "cell_ids",
            "compression": "none",
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=dggs)
        with pytest.raises(ValidationError):
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
        with pytest.raises(ValidationError):
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

    def test_validate_semiminor_axis(self, schema):
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

    def test_validate_duplicate_ellipsoid(self, schema):
        ellipsoid = {
            "name": "WGS84",
            "semi_major_axis": 6378137.0,
            "inverse_flattening": 298.257223563,
            "radius": 6370997.0,
        }
        data = embed_attributes(
            zarr_conventions=[convention_metadata],
            dggs=self.dggs_metadata | {"ellipsoid": ellipsoid},
        )

        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)

    def test_validate_duplicate_inverse_flattening(self, schema):
        ellipsoid = {
            "name": "WGS84",
            "semi_major_axis": 6378137.0,
            "inverse_flattening": 298.257223563,
            "semi_minor_axis": 6356000.0,
        }
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
