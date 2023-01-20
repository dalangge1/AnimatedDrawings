# Animated Drawings
This repo contains companion code for the paper, `A Method for Automatically Animating Children's Drawings of the Human Figure.'
In addition, this repo aims to be a useful creative tool in it's own right, allowing you to create your own animated drawings from your own computer. 

## Installation (To be expanded later)
1. create virtual env
2. pip install -e .
3. Install torchserve's java dependency 
4. Obtain .mar files

## Running (To be expanded later)

### Using the Rendering code
We provide some example top-level configuration files (or 'mvc_configs') to demonstrate how to run the rendering code.
Scenes are created and rendered according to the parmaeters within the mvc_config.
To see for yourself, run the following python commands from within the AnimatedDrawings root directory:

    from animated_drawings import render

    render.start(./examples/config/mvc/interactive_window_example.yaml)

If everything is installed correctly, an interactive window should appear on your screen. 
(Use space to pause/unpause the scene, arrow keys to move back and forth in time, and q to close the screen.)

<img src='./media/interactive_window_example.gif' width="256" height="256" /> </br></br></br>


Suppose you'd like to save the animation as a video file instead of viewing it directly in a window. Specify a different example mvc_config:

    from animated_drawings import render

    render.start('./examples/config/mvc/export_mp4_example.yaml')

You should see a file, video.mp4, located in the same directory as your script.

<img src='./media/mp4_export_video.gif' width="256" height="256" /> </br></br></br>

Perhaps you'd like a tranparent .gif instead of an .mp4? Use this:

    from animated_drawings import render

    render.start('./examples/config/mvc/export_gif_example.yaml')

You'll find video.gif residing within the same directory as your script.

<img src='./media/gif_export_video.gif' width="256" height="256" /> </br></br></br>


### Creating an animation from an image
All of the above examples use drawings with pre-existing annotations.
But suppose you'd like to create an animation starring your own drawing? 
We provide an example script specifically for that purpose.
We use torchserve to pass data to our models, so you'll need to ensure it's properly installed first.
Run the following commands, starting from the AnimatedDrawings root directory:

    # ensure torchserve is running
    cd torchserve
    ./torchserve_start.sh

    cd ../examples
    python image_to_animation.py drawings/garlic.png garlic_out

As you waited, the image located at `drawings/garlic.png` was analyzed, the character detected, segmented, and rigged, and it was animated using BVH motion data from a human actor.
The animation was saved as `./garlic_out/video.gif`.

<img src='./examples/drawings/garlic.png' height="256" /><img src='./media/garlic.gif' width="256" height="256" /></br></br></br>
We provid
- Run torchserve script

### Adding multiple characters to scene
TBD

### Adding multiple characters to scene
TBD

### Fixing bad predictions
TBD

### Adding addition types of motion
TBD

### Example outputs and config files
While our torchserve model's don't predict keypoints for non-humanoid skeletons, you could create them manually and create a custom `retarget_cfg` to retarget motion onto its joints.
Likewise, custom `retarget_cfg` files can be written to support non-humanoid BVH skeletons.
Examples to be added in the future.





