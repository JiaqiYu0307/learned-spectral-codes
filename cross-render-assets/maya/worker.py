"""Maya/Arnold single-pass worker. Run only through Maya's mayapy."""

import argparse
import json
import os
import sys

import maya.standalone


def fail(message):
    raise RuntimeError(message)


def set_if_exists(cmds, plug, value):
    if not cmds.objExists(plug):
        return
    if isinstance(value, str):
        cmds.setAttr(plug, value, type="string")
    elif isinstance(value, (list, tuple)) and len(value) == 3:
        cmds.setAttr(plug, *[float(v) for v in value], type="double3")
    else:
        cmds.setAttr(plug, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    args = parser.parse_args()
    with open(args.job, "r", encoding="utf-8") as handle:
        job = json.load(handle)

    maya.standalone.initialize(name="python")
    import maya.cmds as cmds

    try:
        cmds.file(job["scene"], open=True, force=True, prompt=False)
        if not cmds.pluginInfo("mtoa", query=True, loaded=True):
            cmds.loadPlugin("mtoa", quiet=True)

        required_nodes = [job["camera"], job["light_shape"]]
        required_nodes += [item["transform"] for item in job["objects"].values()]
        required_nodes += [item["file_node"] for item in job["objects"].values()]
        missing = [node for node in required_nodes if not cmds.objExists(node)]
        if missing:
            fail("Missing Maya nodes: " + ", ".join(missing))

        keep_transforms = {item["transform"] for item in job["objects"].values()}
        mesh_shapes = cmds.ls(type="mesh", long=True, noIntermediate=True) or []
        for shape in mesh_shapes:
            parent = (cmds.listRelatives(shape, parent=True, fullPath=False) or [None])[0]
            if parent and parent not in keep_transforms and cmds.objExists(parent):
                set_if_exists(cmds, parent + ".visibility", False)

        for camera_shape in cmds.ls(type="camera") or []:
            set_if_exists(cmds, camera_shape + ".renderable", False)
        camera_shapes = cmds.listRelatives(job["camera"], shapes=True, type="camera") or []
        if len(camera_shapes) != 1:
            fail(f"Expected one camera shape under {job['camera']}, found {camera_shapes}")
        camera_shape = camera_shapes[0]
        set_if_exists(cmds, camera_shape + ".renderable", True)

        for item in job["objects"].values():
            texture = item["texture"]
            if not os.path.isfile(texture):
                fail("Missing texture: " + texture)
            file_node = item["file_node"]
            set_if_exists(cmds, file_node + ".fileTextureName", texture.replace("\\", "/"))
            set_if_exists(cmds, file_node + ".colorSpace", "Raw")
            set_if_exists(cmds, file_node + ".ignoreColorSpaceFileRules", True)
            set_if_exists(cmds, file_node + ".aiAutoTx", False)

        set_if_exists(cmds, job["light_shape"] + ".color", job["light_rgb"])
        set_if_exists(cmds, job["light_shape"] + ".intensity", float(job["light_intensity"]))
        set_if_exists(cmds, job["light_shape"] + ".aiExposure", 0.0)

        set_if_exists(cmds, "defaultRenderGlobals.currentRenderer", "arnold")
        set_if_exists(cmds, "defaultRenderGlobals.animation", False)
        set_if_exists(cmds, "defaultRenderGlobals.imageFilePrefix", job["output_prefix"].replace("\\", "/"))
        set_if_exists(cmds, "defaultResolution.width", int(job["width"]))
        set_if_exists(cmds, "defaultResolution.height", int(job["height"]))
        set_if_exists(cmds, "defaultArnoldRenderOptions.AASamples", int(job["camera_aa_samples"]))
        set_if_exists(cmds, "defaultArnoldRenderOptions.renderDevice", 1 if job["use_gpu"] else 0)
        set_if_exists(cmds, "defaultArnoldRenderOptions.abortOnLicenseFail", True)
        set_if_exists(cmds, "defaultArnoldRenderOptions.autotx", False)
        set_if_exists(cmds, "defaultArnoldRenderOptions.textureAcceptUntiled", True)
        set_if_exists(cmds, "defaultArnoldRenderOptions.textureAcceptUnmipped", True)
        set_if_exists(cmds, "defaultArnoldDriver.aiTranslator", "exr")
        set_if_exists(cmds, "defaultArnoldDriver.halfPrecision", False)
        set_if_exists(cmds, "defaultArnoldDriver.mergeAOVs", True)
        set_if_exists(cmds, "defaultArnoldDriver.colorManagement", 0)
        cmds.currentTime(int(job["frame"]), edit=True)

        os.makedirs(os.path.dirname(job["output_prefix"]), exist_ok=True)
        cmds.arnoldRender(
            seq="",
            w=int(job["width"]),
            h=int(job["height"]),
            cam=camera_shape,
            srv=False,
        )
        candidates = [
            job["output_prefix"] + ".exr",
            job["output_prefix"] + "_1.exr",
            job["output_prefix"] + ".0001.exr",
        ]
        existing = [path for path in candidates if os.path.isfile(path)]
        if not existing:
            fail("Arnold finished but expected EXR was not found: " + ", ".join(candidates))
        print("MAYA_SPECTRAL_OUTPUT=" + existing[0])
    finally:
        cmds.file(new=True, force=True)
        maya.standalone.uninitialize()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("MAYA_SPECTRAL_ERROR=" + str(exc), file=sys.stderr)
        raise
