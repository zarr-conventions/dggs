# Discrete Global Grid System Attribute Convention for Zarr

- **UUID**: 7b255807-140c-42ca-97f6-7a1cfecdbc38
- **Name**: dggs
- **Schema**: "https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v0.1.0/schema.json"
- **Extension Maturity Classification**: Proposal
- **Owner**: @keewis

## Description

This convention describes a JSON object that encodes the coordinate and grid parameters of a discrete global grid system (DGGS) under the `dggs` key in the attributes of zarr groups and arrays.

## Inheritance Model

The `dggs` convention object follows a simple group-to-array inheritance model that should be understood first:

### Inheritance Rules

1. **Group-level definition** (recommended): When the `dggs` convention is defined at the group level, it applies to all arrays that are direct children of that group. It does not apply to groups or arrays deeper in the hierarchy (e.g., grandchildren).
2. **Array-level override**: An array can completely override the group's `dggs` convention with its own definition.
3. **Partial replacement**: Partial inheritance (overriding only some fields while inheriting others) is not allowed.

## Configuration

The configuration in the Zarr convention metadata can be used in these parts of the Zarr hierarchy:

- [x] Group
- [x] Array

|          | Type     | Description       | Required     | Reference     |
| -------- | -------- | ----------------- | ------------ | ------------- |
| **dggs** | `object` | The grid metadata | &#10003; Yes | [dggs](#dggs) |

### Field Details

#### dggs

Object representing the conrete instance of the discrete global grid system.

- **Type**: `object`
- **Required**: &#10003; Yes

This field SHALL describe the concrete instance of the discrete global grid system. See the [DGGS Object](#dggs-object) section below for details.

### DGGS Object

|                       | Type      | Description                                  | Required     | Reference                               |
| --------------------- | --------- | -------------------------------------------- | ------------ | --------------------------------------- |
| **name**              | `string`  | The lower-cased name of the DGGS.            | &#10003; Yes | [name](#name)                           |
| **refinement_level**  | `integer` | The refinement level as an unsigned integer. | &#10003; Yes | [refinement_level](#refinement_level)   |
| **ellipsoid**         | `object`  | The ellipsoid used as a reference body.      | &#10005; No  | [ellipsoid](#ellipsoid)                 |
| **spatial_dimension** | `string`  | Name of the spatial dimension                | &#10003; Yes | [spatial_dimension](#spatial_dimension) |
| **coordinate**        | `string`  | Name of the coordinate                       | &#10003; No  | [coordinate](#coordinate)               |
| **compression**       | `string`  | Compression type of the coordinate           | &#10003; Yes | [compression](#compression)             |

Additional DGGS-specific parameters are allowed.

#### name

The canonical name of the DGGS, normalized to a lower-cased string.

- **Type**: `string`
- **Required**: &#10003; Yes

#### refinement_level

Also called the "depth" or "order", this parameter describes the size of the DGGS cells.

- **Type**: `integer | null`
- **Required**: &#10003; Yes

It MUST only be `null` if the associated coordinate is variable-sized.

#### ellipsoid

The ellipsoid describes the reference system of the DGGS. See the [ellipsoid object](ellipsoid-object) for more information.

- **Type**: `object`
- **Required**: &#10005; No

If not given, a sphere with a radius of `6370997 m` SHALL be assumed.

#### spatial_dimension

The name of spatial dimension.

- **Type**: `string`
- **Required**: &#10003; Yes

#### coordinate

`coordinate` points to the array containing the cell ids. If not provided, the entire domain must be covered and the `refinement_level` MUST NOT be `null`.

- **Type**: `string`
- **Required**: &#10005; No

#### compression

`compression` describes the cell id compression method chosen. It SHALL only be provided if the `coordinate` was provided. If `refinement_level` is `null`, `compression` SHALL be `"none"`.

Uncompressing the cell ids SHALL result in an array of the same length as the `spatial_dimension`.

- **Type**: `string`
- **Required**: &#10005; No

The following values are possible:

- `"none"`: the array referenced by `coordinate` MUST be 1-dimensional and have the same size as the `spatial_dimension`.
- `"compacted"`: the array referenced by `coordinate` MUST be 1-dimensional.
- `"ranges"`: the array referenced by `coordinate` MUST have a shape of `(n_ranges, 2)` that describes the contiguous ranges covered.

### Ellipsoid object

|                        | Type     | Description                             | Required    |
| ---------------------- | -------- | --------------------------------------- | ----------- |
| **name**               | `string` | Human-readable name of the ellipsoid    | No          |
| **semimajor_axis**     | `number` | The semimajor axis of the ellipsoid     | Yes         |
| **semiminor_axis**     | `number` | The semiminor axis of the ellipsoid     | Conditional |
| **inverse_flattening** | `number` | The inverse flattening of the ellipsoid | Conditional |

`semiminor_axis` and `inverse_flattening` are mutually exclusive. If none of them are given, a sphere SHALL be assumed. `name` SHOULD be provided if it exists.

## Examples

### HEALPix

Uncompressed subdomain:

```json
{
  "attributes": {
    "zarr_conventions_version": "0.1.0",
    "zarr_conventions": {
      "7b255807-140c-42ca-97f6-7a1cfecdbc38": {
        "version": "0.1.0",
        "schema": "https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v0.1.0/schema.json",
        "name": "dggs",
        "description": "Discrete Global Grid Systems convention for zarr",
        "spec": "https://github.com/zarr-conventions/dggs/blob/v0.1.0/README.md"
      }
    },
    "dggs": {
      "name": "healpix",
      "refinement_level": 10,
      "indexing_scheme": "nested",
      "spatial_dimension": "cells",
      "ellipsoid": {
        "name": "wgs84",
        "semimajor_axis": 6378137.0,
        "inverse_flattening": 298.257223563
      },
      "coordinate": "cell_ids",
      "compression": "none"
    }
  }
}
```

Full domain, spherical, missing coordinate:

```json
{
  "attributes": {
    "zarr_conventions_version": "0.1.0",
    "zarr_conventions": {
      "7b255807-140c-42ca-97f6-7a1cfecdbc38": {
        "version": "0.1.0",
        "schema": "https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v0.1.0/schema.json",
        "name": "dggs",
        "description": "Discrete Global Grid Systems convention for zarr",
        "spec": "https://github.com/zarr-conventions/dggs/blob/v0.1.0/README.md"
      }
    },
    "dggs": {
      "name": "healpix",
      "refinement_level": 16,
      "indexing_scheme": "nested",
      "spatial_dimension": "cells"
    }
  }
}
```

## Acknowledgements

This template is based on the [STAC extensions template](https://github.com/stac-extensions/template/blob/main/README.md).
