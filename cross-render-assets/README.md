# Website render assets

The `*/native` folders contain original, clean render previews copied from the experiment's `DE2K_Source_Data`. The website uses lossless WebP conversions at exactly the source dimensions. No upscaling or baked lighting insets are used.

The Blender source previews were exported from the linear workflow without display encoding. Website versions are encoded with the standard IEC 61966-2-1 sRGB transfer curve; matching PNGs are stored in `blender/gamma-corrected`. The native inputs remain unchanged in `blender/native`.

| Renderer | Case | Native resolution |
| --- | --- | --- |
| Blender | Broadband | 1080 × 1080 |
| Maya Arnold | Light 0099 | 960 × 540 |
| KeyShot | Pink sky | 1280 × 960 |
| Unreal | Lights 492, 352, 99 | 1920 × 1080 |

`prepare_web_assets.py` copies the render images and generates external illumination panels from the original spectra or environment image. `provenance.json` records source paths and dimensions.

## Maya high-resolution attempt

`maya/render_web.py` prepares an isolated 1920 × 1080 batch render without saving changes to the source scene. The first RGB pass failed because Arnold could not obtain a batch rendering license; see `maya/jh_rgb.log`. No new rendered output was substituted into the website. The original Maya project documents an interactive RenderView workflow, which requires a running licensed Maya GUI session; none was running during this update.

With an available Arnold batch license, run `python render-assets/maya/render_web.py --all` from the workspace. This produces EXR passes only; they still require the experiment's spectral decoding and display conversion before being used on the website.
