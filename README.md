# BlenderIsoRender (Blender 3.0+ I guess?)
A simple utility to render out sprites from an animated model in blender.

~~Currently very primitive~~, you can set some basic camera properties, pick how many angles you want to render from, and render each frame for each angle to a png file in a given location with a prefix.

Update;  I would consider this now essentially feature-complete, there are some QoL features I could and may eventually add, but this is usable in it's current state.

The sprite sheet/atlas generation and packing will likely not become part of this plugin, the features I want from that would be tough to fit within the scope of blenders python, I will make this an external utility and not necessarily in python either.

#### TODO
- [X] Ability to render only keyframes or specific frame intervals
- [ ] Better camera control (currently built with ortho projection in mind, no control over perspective fov only focal length)
- [ ] More rendering options (easy toggle 'shadeless' mode?)
- [ ] Calculate focal length given input of blender unit -> pixel height ratio
- [ ] ~~Create sprite sheet/atlas instead of just individual images~~ - Will be an external tool
- [ ] ~~Tightly pack atlas with metadata file (?)~~ - Will be an external tool


![An image of the GUI for this tool](https://i.imgur.com/TnCsV2x.png)
![An image of the individual sprites rendered with this tool](https://i.imgur.com/0hncIAw.png)
