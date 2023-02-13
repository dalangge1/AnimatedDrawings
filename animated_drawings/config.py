from __future__ import annotations
import logging
from collections import defaultdict
from pathlib import Path
from typing import Union, List, Tuple, Dict, TypedDict
import yaml
from pkg_resources import resource_filename
from animated_drawings.utils import resolve_ad_filepath


class Config():

    def __init__(self, user_mvc_cfg_fn: str) -> None:
        # get the base mvc config
        with open(resource_filename(__name__, "mvc_base_cfg.yaml"), 'r') as f:
            base_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})  # pyright: ignore[reportUnknownMemberType])

        # search for the user-specified mvc confing
        user_mvc_cfg_p: Path = resolve_ad_filepath(user_mvc_cfg_fn, 'user mvc config')
        logging.info(f'Using user-specified mvc config file located at {user_mvc_cfg_p.resolve()}')
        with open(str(user_mvc_cfg_p), 'r') as f:
            user_cfg = defaultdict(dict, yaml.load(f, Loader=yaml.FullLoader) or {})  # pyright: ignore[reportUnknownMemberType]

        # overlay user specified mvc options onto base mvc, use to generate subconfig classes
        self.view: ViewConfig = ViewConfig({**base_cfg['view'], **user_cfg['view']})
        self.scene: SceneConfig = SceneConfig({**base_cfg['scene'], **user_cfg['scene']})
        self.controller: ControllerConfig = ControllerConfig({**base_cfg['controller'], **user_cfg['controller']})

        # cannot use an interactive controller with a headless mesa viewer
        if self.controller.mode == 'interact':
            try:
                assert self.view.use_mesa == False, 'cannot use interactive controller when USE_MESA is True'
            except AssertionError as e:
                msg = f'Config error: {e}'
                logging.critical(msg)
                assert False, msg

        # TODO check if video render controller, then output video path cannot be none
        # TODO if video render and .mp4,  codec cannot be none


class SceneConfig():

    def __init__(self, scene_cfg: dict) -> None:

        # show or hide the floor
        try:
            self.add_floor: bool = scene_cfg['ADD_FLOOR']
            assert isinstance(self.add_floor, bool), 'is not bool'
        except (AssertionError, ValueError) as e:
            msg = f'Error in ADD_FLOOR config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # show or hide visualization of BVH motion driving characters
        try:
            self.add_ad_retarget_bvh: bool = scene_cfg['ADD_AD_RETARGET_BVH']
            assert isinstance(self.add_ad_retarget_bvh, bool), 'is not bool'
        except (AssertionError, ValueError) as e:
            msg = f'Error in ADD_AD_RETARGET_BVH config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # config files for characters, driving motions, and retargeting
        self.animated_characters: List[Tuple[CharacterConfig, RetargetConfig, MotionConfig]] = []

        each: Dict[str, str]
        for each in scene_cfg['ANIMATED_CHARACTERS']:
            char_cfg_fn: str = each['character_cfg']
            motion_cfg_fn: str = each['motion_cfg']
            retarget_cfg_fn:str = each['retarget_cfg']
            self.animated_characters.append((
                CharacterConfig(char_cfg_fn),
                RetargetConfig(retarget_cfg_fn),
                MotionConfig(motion_cfg_fn)
            ))

        #self.animated_characters: list[dict[str, str]] = scene_cfg['ANIMATED_CHARACTERS']
        # try:
        #     for dict_ in self.animated_characters:
        #         assert 'character_cfg' in dict_.keys(), 'missing character_cfg'
        #         assert 'motion_cfg' in dict_.keys(), 'missing motion_cfg'
        #         assert 'retarget_cfg' in dict_.keys(), 'missing retarget_cfg'
        # except AssertionError as e:
        #     msg = f'Error in ANIMATED_CHARACTERS config parameter: {e}'
        #     logging.critical(msg)
        #     assert False, msg


class ViewConfig():

    def __init__(self, view_cfg: dict) -> None:

        # set color used to clear render buffer
        try:
            self.clear_color: list[Union[float, int]] = view_cfg["CLEAR_COLOR"]
            assert len(self.clear_color) == 4, 'length not four'
            for val in self.clear_color:
                assert isinstance(val, (float, int)), f'{val} not float or int'
                assert val <= 1.0, 'values must be <= 1.0'
                assert val >= 0.0, 'values must be >= 0.0'
        except (AssertionError, ValueError) as e:
            msg = f'Error in CLEAR_COLOR config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set an image to use for the background, if desired
        try:
            self.background_image: Union[None, str] = view_cfg["BACKGROUND_IMAGE"]
            assert isinstance(self.background_image, (NoneType, str)), 'type not NoneType or str'
        except (AssertionError, ValueError) as e:
            msg = f'Error in BACKGROUND_IMAGE config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set the dimensions of the window or output video
        try:
            self.window_dimensions: tuple[int, int] = view_cfg["WINDOW_DIMENSIONS"]
            assert len(self.window_dimensions) == 2, 'length is not 2'
            for val in self.window_dimensions:
                assert val > 0, f'{val} must be > 0'
                assert isinstance(val, int), 'type not int'
        except (AssertionError, ValueError) as e:
            msg = f'Error in WINDOW_DIMENSIONS config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want the character rigs to be visible
        try:
            self.draw_ad_rig: bool = view_cfg['DRAW_AD_RIG']
            assert isinstance(self.draw_ad_rig, bool), 'value is not bool type'
        except (AssertionError, ValueError) as e:
            msg = f'Error in DRAW_AD_RIG config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want the character textures to be visible
        try:
            self.draw_ad_txtr: bool = view_cfg['DRAW_AD_TXTR']
            assert isinstance(self.draw_ad_txtr, bool), 'value is not bool type'
        except (AssertionError, ValueError) as e:
            msg = f'Error in DRAW_AD_TXTR config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want the character triangle->bone assignment colors to be visible
        try:
            self.draw_ad_color: bool = view_cfg['DRAW_AD_COLOR']
            assert isinstance(self.draw_ad_color, bool), 'value is not bool type'
        except (AssertionError, ValueError) as e:
            msg = f'Error in DRAW_AD_COLOR config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want the character mesh lines to be visible
        try:
            self.draw_ad_mesh_lines: bool = view_cfg['DRAW_AD_MESH_LINES']
            assert isinstance(self.draw_ad_mesh_lines, bool), 'value is not bool type'
        except (AssertionError, ValueError) as e:
            msg = f'Error in DRAW_AD_MESH_LINES config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set whether we want to use mesa on the back end (necessary for headless rendering)
        try:
            self.use_mesa: bool = view_cfg['USE_MESA']
            assert isinstance(self.use_mesa, bool), 'value is not bool type'
        except (AssertionError, ValueError) as e:
            msg = f'Error in USE_MESA config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set the position of the view camera
        try:
            self.camera_pos: list[Union[float, int]] = view_cfg['CAMERA_POS']
            assert len(self.camera_pos) == 3, 'length != 3'
            for val in self.camera_pos:
                assert isinstance(val, (float, int)), f' {val} is not float or int'
        except (AssertionError, ValueError) as e:
            msg = f'Error in CAMERA_POS config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set the forward vector of the view camera (but it renders out of it's rear)
        try:
            self.camera_fwd: list[Union[float, int]] = view_cfg['CAMERA_FWD']
            assert len(self.camera_fwd) == 3, 'length != 3'
            for val in self.camera_fwd:
                assert isinstance(val, (float, int)), f' {val} is not float or int'
        except (AssertionError, ValueError) as e:
            msg = f'Error in CAMERA_FWD config parameter: {e}'
            logging.critical(msg)
            assert False, msg


class ControllerConfig():

    def __init__(self, controller_cfg: dict) -> None:

        # set controller mode
        try:
            self.mode: str = controller_cfg["MODE"]
            assert isinstance(self.mode, str), 'is not str'
            assert self.mode in ('interactive', 'video_render'), 'mode not interactive or video_render'
        except (AssertionError, ValueError) as e:
            msg = f'Error in MODE config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set timestep for user interactions in interactive mode
        try:
            self.keyboard_timestep: Union[float, int] = controller_cfg["KEYBOARD_TIMESTEP"]
            assert isinstance(self.keyboard_timestep, (float, int)), 'is not floar or int'
            assert self.keyboard_timestep > 0, 'timestep val must be > 0'
        except (AssertionError, ValueError) as e:
            msg = f'Error in KEYBOARD_TIMESTEP config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set output video path (only use in video_render mode)
        try:
            self.output_video_path: Union[None, str] = controller_cfg['OUTPUT_VIDEO_PATH']
            assert isinstance(self.output_video_path, (NoneType, str)), 'type is not None or str'
            if isinstance(self.output_video_path, str):
                assert Path(self.output_video_path).suffix in ('.gif', '.mp4'), 'output video extension not .gif or .mp4 '
        except (AssertionError, ValueError) as e:
            msg = f'Error in OUTPUT_VIDEO_PATH config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # set output video codec (only use in video_render mode with .mp4)
        try:
            self.output_video_codec: Union[None, str] = controller_cfg['OUTPUT_VIDEO_CODEC']
            assert isinstance(self.output_video_codec, (NoneType, str)), 'type is not None or str'
        except (AssertionError, ValueError) as e:
            msg = f'Error in OUTPUT_VIDEO_CODEC config parameter: {e}'
            logging.critical(msg)
            assert False, msg

class CharacterConfig():

    class JointDict(TypedDict):
        loc: List[float]
        name: str
        parent: Union[None, str]

    def __init__(self, char_cfg_fn: str) -> None:
        character_cfg_p = resolve_ad_filepath(char_cfg_fn, 'character cfg')
        with open(str(character_cfg_p), 'r') as f:
            char_cfg = yaml.load(f, Loader=yaml.FullLoader)

        # validate image height
        try:
            self.img_height: int = char_cfg['height']
            assert isinstance(self.img_height, int), 'type not int'
            assert self.img_height > 0, 'must be > 0'
        except (AssertionError, ValueError) as e:
            msg = f'Error in character height config parameter: {e}'
            logging.critical(msg)
            assert False, msg

        # validate image width
        try:
            self.img_width: int = char_cfg['width']
            assert isinstance(self.img_width, int), 'type not int'
            assert self.img_width > 0, 'must be > 0'
        except (AssertionError, ValueError) as e:
            msg = f'Error in character width config parameter: {e}'
            logging.critical(msg)
            assert False, msg
        
        # based on height and width, determine what final img dimension will be (post padding)
        self.img_dim: int = max(self.img_height, self.img_width)
        
        # validate skeleton
        try:
            self.skeleton: List[CharacterConfig.JointDict] = []
            for joint in char_cfg['skeleton']:

                # ensure loc input is valid...
                loc: List[int] = joint['loc']
                assert len(loc) == 2, 'joint loc must be of length 2'
                assert loc[0] >= 0, 'x val must be >= 0'
                assert loc[0] < self.img_width, 'x val must be < image width'
                assert loc[1] >= 0, 'y val must be >= 0'
                assert loc[1] < self.img_height, 'y val must be < image height'

                #... then scale to between 0-1 based on img dim
                loc_x: float = loc[0] / self.img_dim  # width
                loc_y: float = loc[1] / self.img_dim + (1 - self.img_height / self.img_dim)  # height

                # validate joint name
                name: str = joint['name']
                assert isinstance(name, str), 'name must be str'

                # validate joint parent
                parent: Union[None, str] = joint['parent']
                assert isinstance(parent, (NoneType, str)), 'parent must be str or NoneType'

                self.skeleton.append({'loc': [loc_x, loc_y], 'name': name, 'parent': parent})
        except AssertionError as e:
            msg = f'Error in character skeleton: {e}'
            logging.critical(msg)
            assert False, msg
        
        # validate skeleton joint parents
        try:
            names: List[str] = [joint['name'] for joint in self.skeleton]
            for joint in self.skeleton:
                assert isinstance(joint['parent'], NoneType) or joint['parent'] in names, f'joint.parent not None and not valid joint name: {joint}'
        except AssertionError as e:
            msg = f'Error in character skeleton: {e}'
            logging.critical(msg)
            assert False, msg   

        # validate mask and texture files
        try:
            self.mask_p: Path = character_cfg_p.parent / 'mask.png'
            self.txtr_p: Path = character_cfg_p.parent / 'texture.png'
            assert self.mask_p.exists(), f'cannot find character mask: {self.mask_p}'
            assert self.txtr_p.exists(), f'cannot find character texture: {self.txtr_p}'
        except AssertionError as e:
            msg = f'Error validating character files: {e}'
            logging.critical(msg)
            assert False, msg   

class MotionConfig():

    def __init__(self, motion_cfg_fn: str) -> None:
        motion_cfg_p = resolve_ad_filepath(motion_cfg_fn, 'motion cfg')
        with open(str(motion_cfg_p), 'r') as f:
            motion_cfg = yaml.load(f, Loader=yaml.FullLoader)

        # validate start_frame_idx
        try:
            self.start_frame_idx: int = motion_cfg.get('start_frame_idx', 0)
            assert self.start_frame_idx >= 0, 'start_frame_idx must be > 0'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating start_frame_idx: {e}'
            logging.critical(msg)
            assert False, msg           

        # validate end_frame_idx
        try:
            self.end_frame_idx: int = motion_cfg.get('end_frame_idx', None)
            assert self.end_frame_idx >= self.start_frame_idx, 'end_frame_idx must be > start_frame_idx'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating end_frame_idx: {e}'
            logging.critical(msg)
            assert False, msg      

        # validate groundplane joint
        try:
            self.groundplane_joint: str = motion_cfg['groundplane_joint']
            assert isinstance(self.groundplane_joint, str), 'groundplane joint must be str'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating groundplane joint: {e}'
            logging.critical(msg)
            assert False, msg  
        
        # validate forward_perp_joint_vectors
        try:
            self.forward_perp_joint_vectors: List[Tuple[str, str]] = motion_cfg['forward_perp_joint_vectors']
            assert len(self.forward_perp_joint_vectors) > 0, 'forward_perp_joint_vectors len must be > 0'
            for each in self.forward_perp_joint_vectors:
                assert len(each) == 2, 'each list in forrward_perp_joint_vectors must have len = 2'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating forward_perp_joint_vectors: {e}'
            logging.critical(msg)
            assert False, msg  
        #TODO: check that all joints within forward perp joint vectors are valid bvh joints

        # validate scale 
        try:
            self.scale: float = motion_cfg['scale']
            assert isinstance(self.scale, (int, float)), 'scale must be float or int'
            assert self.scale > 0, 'scale must be > 0'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating scale: {e}'
            logging.critical(msg)
            assert False, msg              
        
        # validate up
        try:
            self.up: str = motion_cfg['up']
            assert self.up in ['+y', '+z'], 'up must be "+y" or "+z'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating up: {e}'
            logging.critical(msg)
            assert False, msg  
        
        # validate bvh_p
        try:
            self.bvh_p: Path = resolve_ad_filepath(motion_cfg['filepath'], 'bvh filepath')
        except (AssertionError, ValueError) as e:
            msg = f'Error validating bvh_p: {e}'
            logging.critical(msg)
            assert False, msg  


class RetargetConfig():

    class BvhProjectionBodypartGroup(TypedDict):
        bvh_joint_names: List[str]
        method: str
        name: str

    class CharBodypartGroup(TypedDict):
        bvh_depth_drivers: List[str]
        char_joints: List[str]

    class CharBvhRootOffset(TypedDict):
        bvh_projection_bodypart_group_for_offset: str
        bvh_joints: List[List[str]]
        char_joints: List[List[str]]

    def __init__(self, retarget_cfg_fn: str) -> None:
        retarget_cfg_p = resolve_ad_filepath(retarget_cfg_fn, 'retarget cfg')
        with open(str(retarget_cfg_p), 'r') as f:
            retarget_cfg = yaml.load(f, Loader=yaml.FullLoader)
        
        # validate character starting location
        try:
            self.char_start_loc = retarget_cfg['char_starting_location']
            assert len(self.char_start_loc) == 3, 'char start loc must be of len 3'
            for val in self.char_start_loc:
                assert isinstance(val, (float, int)), 'type must be float or int'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating char start location: {e}'
            logging.critical(msg)
            assert False, msg   

        # validate bvh project bodypart groups
        self.bvh_projection_bodypart_groups: List[RetargetConfig.BvhProjectionBodypartGroup]
        try:
            self.bvh_projection_bodypart_groups = retarget_cfg['bvh_projection_bodypart_groups']

            for group in self.bvh_projection_bodypart_groups:
                assert group['method'] in ['pca', 'saggital', 'frontal'], 'group method must be "pca", "saggital", or "frontal"'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating bvh_projection_bodypart_groups: {e}'
            logging.critical(msg)
            assert False, msg   
        # TODO: Check that joints within bvh_joint_names all exist within the BVH skeleton
        # TODO: Check that group names are unique
        
        # validate char bodypart groups
        self.char_bodypart_groups: List[RetargetConfig.CharBodypartGroup]
        try:
            self.char_bodypart_groups = retarget_cfg['char_bodypart_groups']
            for group in self.char_bodypart_groups:
                assert len(group['bvh_depth_drivers']) > 0, 'bvh_depth_drivers must have at least one joint specified'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating char_bodypart_groups: {e}'
            logging.critical(msg)
            assert False, msg   
        # TODO: Check that bvh joint drivers are valid bvh joints
        # TODO: Check that all char_joints are valid character joints

        # validate char bvh root offset
        self.char_bvh_root_offset: RetargetConfig.CharBvhRootOffset
        try:
            self.char_bvh_root_offset = retarget_cfg['char_bvh_root_offset']
            assert len(self.char_bvh_root_offset['bvh_joints']) > 0, 'bvh_joints list must be greater than zero' 
            for each in self.char_bvh_root_offset['bvh_joints']:
                assert len(each) > 0, 'each list in bvh_joints must have len > 0'

            assert len(self.char_bvh_root_offset['char_joints']) > 0, 'char_joints list must be greater than zero' 
            for each in self.char_bvh_root_offset['char_joints']:
                assert len(each) > 0, 'each list in char_joints must have len > 0'
            
            assert isinstance(self.char_bvh_root_offset['bvh_projection_bodypart_group_for_offset'], str), 'bvh_projection_bodypart_group_for_offset must be str'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating char_bvh_root_offset: {e}'
            logging.critical(msg)
            assert False, msg   
        #TODO check that bvh_projection_bodypart_group_for_offset matches a bvh_projection_bodypart_group name
        #TODO: check these are valid bvh_joints: List[List[str]]
        #TODO: check these are valid char_joint: List[List[str]]

        # validate char joint bvh joints mapping
        self.char_joint_bvh_joints_mapping: Dict[str, Tuple[str, str]]
        try:
            self.char_joint_bvh_joints_mapping = retarget_cfg['char_joint_bvh_joints_mapping']
            for key, val in self.char_joint_bvh_joints_mapping.items():
                assert isinstance(key, str), 'key must be str'
                assert isinstance(val, tuple), 'val must be tuple'
                assert len(val) == 2, 'val must be of len 2'
                assert isinstance(val[0], str) and isinstance(val[1], str), 'values must be str'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating char_bvh_root_offset: {e}'
            logging.critical(msg)
            assert False, msg              

        # TODO: check that dict keys correspond to valid character joints
        # TODO: check that dict values correspond to valid bvh joint

        # validate char runtime checks
        self.char_runtime_checks: List[str]
        try:
            self.char_runtime_checks = retarget_cfg['char_runtime_checks']
            for check in self.char_runtime_checks:

                assert check[0] in ['above'], 'currently only above check is supported'
                if check[0] == 'above':
                    assert len(check) == 4, 'above check needs 3 additional parameters'
        except (AssertionError, ValueError) as e:
            msg = f'Error validating char_runtime_checks: {e}'
            logging.critical(msg)
            assert False, msg             

        # TODO: check that, if above test, following 3 params are valid character joint names

NoneType = type(None)  # needed for type checking
