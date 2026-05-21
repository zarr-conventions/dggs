import json
import pathlib
import pytest
import jsonschema
from jsonschema.exceptions import ValidationError

JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

@pytest.fixture
def schema():
    path = pathlib.Path(__file__).parent.parent / "schema.json"
    return json.loads(path.read_text())

def embed_attributes(**attrs: JSON) -> JSON:
    return {
        "zarr_format": 3,
        "node_type": "group",
        "attributes": attrs
    }

convention_metadata =       {
        "schema_url": "https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v1/schema.json",
        "spec_url": "https://github.com/zarr-conventions/dggs/blob/v1/README.md",
        "uuid": "7b255807-140c-42ca-97f6-7a1cfecdbc38",
        "name": "dggs",
        "description": "Discrete Global Grid Systems convention for zarr"
      }


def test_schema(schema):
    validator = jsonschema.validators.validator_for(schema)
    validator.check_schema(schema)

def test_validate_missing_convention_declaration(schema):
    data: JSON = embed_attributes(dggs={
              "name": "h3",
              "refinement_level": 10,
              "spatial_dimension": "cell",
              "coordinate": "cell_ids",
              "compression": "none"
            }
        )

    with pytest.raises(ValidationError):
        jsonschema.validate(data, schema)

class TestEllipsoid:
    dggs_metadata: ClassVar[JSON] = {
              "name": "h3",
              "refinement_level": 10,
              "spatial_dimension": "cell",
              "coordinate": "cell_ids",
              "compression": "none"
            }

    def test_validate_implicit_sphere(self, schema):
        data: JSON = embed_attributes(zarr_conventions=[convention_metadata], dggs=self.dggs_metadata)
        jsonschema.validate(data, schema)

    def test_validate_semiminor_axis(self, schema):
        ellipsoid = {
            "name": "WGS84",
            "semi_major_axis": 6378137.0,
            "semi_minor_axis": 6356752.314
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=self.dggs_metadata | {"ellipsoid": ellipsoid})
        jsonschema.validate(data, schema)

    def test_validate_inverse_flattening(self, schema):
        ellipsoid = {
            "name": "WGS84",
            "semi_major_axis": 6378137.0,
            "inverse_flattening": 298.257223563
        }
        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=self.dggs_metadata | {"ellipsoid": ellipsoid})
        jsonschema.validate(data, schema)

    def test_validate_explicit_sphere(self, schema):
        ellipsoid = {
            "name": "sphere",
            "radius": 6370997.0
        }

        data = embed_attributes(zarr_conventions=[convention_metadata], dggs=self.dggs_metadata | {"ellipsoid": ellipsoid})
        jsonschema.validate(data, schema)

    def test_validate_duplicate_ellipsoid(self, schema):
        ellipsoid = {
            "name": "WGS84",
            "semi_major_axis": 6378137.0,
            "inverse_flattening": 298.257223563,
            "radius": 6370997.0
        }
        data = embed_attributes(
            zarr_conventions=[convention_metadata],
            dggs=self.dggs_metadata | {"ellipsoid": ellipsoid}
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
            dggs=self.dggs_metadata | {"ellipsoid": ellipsoid}
        )

        with pytest.raises(ValidationError):
            jsonschema.validate(data, schema)
