# Discrete Global Grid System Attribute Convention for Zarr

- **UUID**: 7b255807-140c-42ca-97f6-7a1cfecdbc38
- **Name**: dggs
- **Schema URL**: https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v1/schema.json
- **Spec URL**: https://github.com/zarr-conventions/dggs/blob/v1/README.md
- **Extension Maturity Classification**: Pilot
- **Owner**: @keewis

## Description

This convention describes a JSON object that encodes the coordinate and grid parameters of a discrete global grid system (DGGS) under the `dggs` key in the attributes of zarr groups and arrays.

It is inspired by the CF conventions' `healpix` grid mapping (first included in version 1.13), but deliberately makes different choices in some cases to be more broadly useful in the zarr ecosystem.

Examples:

- [`healpix` on WGS84](examples/healpix-ellipsoid-inverse-flattening.json)
- [Full domain `healpix` with an implict sphere](examples/healpix-full_domain-implicit-sphere.json)
- [`h3` with an explicit sphere](examples/h3-explicit-sphere.json)
- [Composition with `multiscales`](examples/multiscales.json)

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

This field MUST describe the concrete instance of the discrete global grid system. See the [DGGS Object](#dggs-object) section below for details.

### DGGS Object

|                       | Type      | Description                                  | Required     | Reference                               |
| --------------------- | --------- | -------------------------------------------- | ------------ | --------------------------------------- |
| **name**              | `string`  | The lower-cased name of the DGGS.            | &#10003; Yes | [name](#name)                           |
| **refinement_level**  | `integer` | The refinement level as an unsigned integer. | &#10003; Yes | [refinement_level](#refinement_level)   |
| **ellipsoid**         | `object`  | The ellipsoid used as a reference body.      | &#10005; No  | [ellipsoid](#ellipsoid)                 |
| **spatial_dimension** | `string`  | Name of the spatial dimension                | &#10003; Yes | [spatial_dimension](#spatial_dimension) |
| **coordinate**        | `string`  | Name of the coordinate                       | &#10005; No  | [coordinate](#coordinate)               |
| **compression**       | `string`  | Compression type of the coordinate           | Conditional  | [compression](#compression)             |

Additional DGGS-specific parameters are allowed (see [DGGS specific parameters](dggs-specific-parameters)).

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

If not given, a sphere with a radius of `6370997 m` MUST be assumed.

#### spatial_dimension

The name of spatial dimension.

- **Type**: `string`
- **Required**: &#10003; Yes

#### coordinate

`coordinate` points to the array containing the cell ids. If not provided, the entire domain must be covered and the `refinement_level` MUST NOT be `null`.

- **Type**: `string`
- **Required**: &#10005; No

#### compression

`compression` describes the cell id compression method chosen. It MUST only be provided if the `coordinate` was provided. If `refinement_level` is `null`, `compression` MUST be `"none"`.

Uncompressing the cell ids MUST result in an array of the same length as the `spatial_dimension`.

- **Type**: `string`
- **Required**: Conditional

The following values are possible:

- `"none"`: the array referenced by `coordinate` MUST be 1-dimensional and have the same size as the `spatial_dimension`.
- `"compacted"`: the array referenced by `coordinate` MUST be 1-dimensional.
- `"ranges"`: the array referenced by `coordinate` MUST have a shape of `(n_ranges, 2)` that describes the contiguous ranges covered.

### Ellipsoid object

The ellipsoid object is modelled after [`projjson`](https://proj.org/en/stable/specifications/projjson.html)'s definition. It can describe either a sphere or an ellipsoid.

Following `projjson` and WKT the **name** is required to help compare the values in the ellipsoid object against other sources, but should not be used to infer the values. For examples, look for the ellipsoid fields in these CRS definitions:

| Naming Authority                        | URL                                                    |
| --------------------------------------- | ------------------------------------------------------ |
| European Petroleum Survey Groups (EPSG) | http://www.opengis.net/def/crs/EPSG or http://epsg.org |
| International Astronomical Union (IAU)  | http://www.opengis.net/def/crs/IAU                     |
| Open Geospatial Consortium (OGC)        | http://www.opengis.net/def/crs/OGC                     |
| ESRI                                    | https://spatialreference.org/ref/esri/                 |

(taken from the `proj:code` documentation of the [`proj` convention](https://github.com/zarr-conventions/proj))

#### Sphere

|            | Type     | Description                       | Required     |
| ---------- | -------- | --------------------------------- | ------------ |
| **name**   | `string` | Human-readable name of the sphere | &#10003; Yes |
| **radius** | `number` | The radius of the sphere          | &#10003; Yes |

#### Ellipsoid

|                        | Type     | Description                             | Required     |
| ---------------------- | -------- | --------------------------------------- | ------------ |
| **name**               | `string` | Human-readable name of the ellipsoid    | &#10003; Yes |
| **semi_major_axis**    | `number` | The semimajor axis of the ellipsoid     | &#10003; Yes |
| **semi_minor_axis**    | `number` | The semiminor axis of the ellipsoid     | Conditional  |
| **inverse_flattening** | `number` | The inverse flattening of the ellipsoid | Conditional  |

`semi_minor_axis` and `inverse_flattening` are mutually exclusive.

### DGGS specific parameters

Some DGGS have parameters other than `refinement_level`, which can be added to the `dggs` object. This section contains standardized extensions for common DGGS.

#### HEALPix

The HEALPix DGGS (`"name": "healpix"`) has one additional required parameter:

|                     | Type     | Description             | Required     |
| ------------------- | -------- | ----------------------- | ------------ |
| **indexing_scheme** | `string` | HEALPix indexing scheme | &#10003; Yes |

The **indexing_scheme** parameter describes the space-filling curve used to index the cells. For values other than `ring` or `nested` the `refinement_level` must be `null`.

Known values are: `nested`, `ring`, `zuniq`, `nuniq` (but there are many more where the name matches `[a-z_]*uniq`).

## Usage with the [`multiscales`](https://github.com/zarr-conventions/multiscales) convention

The `multiscales` convention allows describing the relationships between the sibling groups in an image pyramid. Since rotations (translations on a sphere or ellipsoid) are not supported, any `transform` objects (as required by the presence of the `derived_from` attribute) MUST contain only a single element `scale` array, and MUST NOT contain a `translation` attribute.

To be fully self-contained, it is recommended to specify the full `dggs` object for the original data. Any derived groups (as indicated by the presence of `derived_from`) MAY then contain a reduced `dggs` object that contains only the changed properties.

## Examples

### HEALPix

Uncompressed subdomain:

```json
{
  "attributes": {
    "zarr_conventions": [
      {
        "schema_url": "https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v1/schema.json",
        "spec_url": "https://github.com/zarr-conventions/dggs/blob/v1/README.md",
        "uuid": "7b255807-140c-42ca-97f6-7a1cfecdbc38",
        "name": "dggs",
        "description": "Discrete Global Grid Systems convention for zarr"
      }
    ],
    "dggs": {
      "name": "healpix",
      "refinement_level": 10,
      "indexing_scheme": "nested",
      "spatial_dimension": "cells",
      "ellipsoid": {
        "name": "WGS84",
        "semi_major_axis": 6378137.0,
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
    "zarr_conventions": [
      {
        "schema_url": "https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v1/schema.json",
        "spec_url": "https://github.com/zarr-conventions/dggs/blob/v1/README.md",
        "uuid": "7b255807-140c-42ca-97f6-7a1cfecdbc38",
        "name": "dggs",
        "description": "Discrete Global Grid Systems convention for zarr"
      }
    ],
    "dggs": {
      "name": "healpix",
      "refinement_level": 16,
      "indexing_scheme": "nested",
      "spatial_dimension": "cells"
    }
  }
}
```

Composition with the `multiscales` convention:

```json
{
  "attributes": {
    "zarr_conventions": [
      {
        "schema_url": "https://raw.githubusercontent.com/zarr-conventions/multiscales/refs/tags/v1/schema.json",
        "spec_url": "https://github.com/zarr-conventions/multiscales/blob/v1/README.md",
        "uuid": "d35379db-88df-4056-af3a-620245f8e347",
        "name": "multiscales",
        "description": "Multiscale layout of zarr datasets"
      },
      {
        "schema_url": "https://raw.githubusercontent.com/zarr-conventions/dggs/refs/tags/v1/schema.json",
        "spec_url": "https://github.com/zarr-conventions/dggs/blob/v1/README.md",
        "uuid": "7b255807-140c-42ca-97f6-7a1cfecdbc38",
        "name": "dggs",
        "description": "Discrete Global Grid Systems convention for zarr"
      }
    ],
    "multiscales": {
      "layout": [
        {
          "asset": "10",
          "dggs": {
            "name": "healpix",
            "refinement_level": 10,
            "indexing_scheme": "nested",
            "spatial_dimension": "cells",
            "ellipsoid": {
              "name": "WGS84",
              "semi_major_axis": 6378137.0,
              "inverse_flattening": 298.257223563
            },
            "coordinate": "cell_ids",
            "compression": "none"
          }
        },
        {
          "asset": "8",
          "derived_from": "10",
          "transform": { "scale": [4.0] },
          "dggs": { "refinement_level": 8 }
        },
        {
          "asset": "4",
          "derived_from": "10",
          "transform": { "scale": [64.0] },
          "dggs": { "refinement_level": 4 }
        }
      ],
      "resampling_method": "average"
    }
  }
}
```

## Acknowledgements

This template is based on the [STAC extensions template](https://github.com/stac-extensions/template/blob/main/README.md).
