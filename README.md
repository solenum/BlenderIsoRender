# BlenderIsoRender (Blender 3.0+ I guess?)
A simple utility to render out sprites from an animated model in blender.

Currently very primitive, you can set some basic camera properties, pick how many angles you want to render from, and render each frame for each angle to a png file in a given location with a prefix.

#### TODO
- [ ] Ability to render only keyframes or specific frame intervals
- [ ] Better camera control (currently built with ortho projection in mind, no control over perspective fov only focal length)
- [ ] More rendering options (easy toggle 'shadeless' mode?)
- [ ] Calculate focal length given input of blender unit -> pixel height ratio


![An image of the GUI for this tool](https://i.imgur.com/x10hCQB.png)
