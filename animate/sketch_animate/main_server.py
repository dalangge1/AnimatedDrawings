import yaml
import os
import logging

if 'SKETCH_ANIMATE_RENDER_BACKEND' in os.environ and \
        os.environ['SKETCH_ANIMATE_RENDER_BACKEND'] == 'OPENGL':
    logging.info('SKETCH_ANIMATE_RENDER_BACKEND == OPENGL. Using OpenGL')
    try:
        from OpenGL import GL
    except:
        logging.critical('Error initializing OpenGL. Aborting')
    logging.info('OpenGL successfully initialized')

else:
    logging.info('SKETCH_ANIMATE_RENDER_BACKEND != OPENGL, Using OSMesa')
    try:
        os.environ['PYOPENGL_PLATFORM'] = "osmesa"
        os.environ['MUJOCO_GL'] = "osmesa"
        os.environ['MESA_GL_VERSION_OVERRIDE'] = "3.3"
        from OpenGL import GL, osmesa
    except:
        logging.critical('Error initializing osmesa. Aborting')
    logging.info('osmesa successfully initialized')

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

import time
from Shapes.Sketch import Sketch, ARAP_Sketch
from Shapes.Floor import Floor
from Shapes.BVH import BVH
from camera import Camera
from util import bodypart_groups
import SceneManager.render_manager as render_manager


def build_cfg(motion_cfg_path):
    with open('../sketch_animate/config/base.yaml', 'r') as f:
        base_cfg = yaml.load(f, Loader=yaml.FullLoader)

    with open(motion_cfg_path, 'r') as f:
        motion_cfg = yaml.load(f, Loader=yaml.FullLoader)

    logging.info(f'loaded motion_cfg: {motion_cfg_path}')

    return {**base_cfg, **motion_cfg}  # combine and overwrite base with user specified config when necessary


def video_from_cfg(character_cfg_path, motion_cfg_path, video_output_path):

    cfg = build_cfg(motion_cfg_path)

    cfg['OUTPUT_PATH'] = str(Path(video_output_path).resolve())

    scene_manager = render_manager.RenderManager(cfg=cfg)

    # first add any background scene elements (depth test is disabled)
    if cfg['DRAW_FLOOR']:
        scene_manager.add(Floor())

    # create BVH skeleton and add to the scene
    bvh = BVH(cfg)
    scene_manager.add_bvh(bvh)

    # create character and add to scene
    character_cfg_path = Path(character_cfg_path)
    with open(character_cfg_path, 'r') as f:
        sketch_cfg = yaml.load(f, Loader=yaml.FullLoader)
        sketch_cfg['image_loc'] = f"{str(character_cfg_path.parent)}/{sketch_cfg['image_name']}"

    ARAP_pickle_loc = os.path.join(Path(sketch_cfg['image_loc']).parent, 'ARAP_Sketch.pickle')
    if os.path.exists(ARAP_pickle_loc):
        logging.info(f'pickled arap_sketch exists. Using it: {ARAP_pickle_loc}')
        arap_sketch = ARAP_Sketch.load_from_pickle(ARAP_pickle_loc)
    else:
        logging.info(f'pickled arap_sketch DNE. Creating it: {ARAP_pickle_loc}')
        arap_sketch = ARAP_Sketch(sketch_cfg, cfg)

    scene_manager.add_sketch(arap_sketch)

    # create root motion transferrer
    scene_manager.create_root_motion_transferrer()

    # add all cameras
    for cam_cfg in cfg['Cameras']:
        if cam_cfg['type'] == 'ignore':
            continue

        cam = Camera(cfg, cam_cfg['cam_pos'], cam_cfg['cam_up'], yaw=cam_cfg['yaw'], name=cam_cfg['name'],
                     cam_type=cam_cfg['type'])

        if cam_cfg['type'] == 'free':
            scene_manager.add_free_camera(cam)
        elif cam_cfg['type'] == 'triangulation':
            scene_manager.add_info_camera(cam)
        elif cam_cfg['type'] == 'sketch':
            scene_manager.add_sketch_camera(cam)
        elif cam_cfg['type'] == 'bvh':
            scene_manager.add_bvh_camera(cam, bodypart_groups[cam_cfg['retarget_bodypart_group']])
        else:
            assert False, 'Unsupported camera type. cam name: {} - cam type: {}'.format(cam_cfg['name'],
                                                                                        cam_cfg['type'])
    scene_manager.run()


if __name__ == '__main__':
    if not os.path.exists(sys.argv[1]):
        assert False, 'Cannot find motion_config: {}'.format(sys.argv[1])

    if not os.path.exists(sys.argv[2]):
        assert False, 'Cannot find sketch_config: {}'.format(sys.argv[2])

    if not os.path.exists(sys.argv[3]):
        assert False, 'Output directory does not exist: {}'.format(sys.argv[3])

    logging.basicConfig(filename='log.txt', level=logging.DEBUG)
    cfg = build_cfg()
    video_from_cfg(cfg)