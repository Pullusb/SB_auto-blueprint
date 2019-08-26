# Auto Blueprint
Generate a blueprint scene of the selected(s) object(s) in one click !
  
**[Download](https://raw.githubusercontent.com/Pullusb/SB_auto-blueprint/master/AutoBlueprint.py)** (right click, save Target as)

**[Download older (2.7)](https://raw.githubusercontent.com/Pullusb/SB_auto-blueprint/master/AutoBlueprint_279.py)** (right click, save Target as)
  
### Description
**layouts available:**
- 2 views aligned: face - side
- 3 views aligned: face - 3/4 - side
- 4 views:         side - face - top - back
- 4 views Show:    side - face - back - isometric (three quarter left/up)

**Options:**
- Considered one object: if ticked, all selected objects will be considered as one to shoot (carefull experimental option, it will simply try to merge object, you may want to do it manually and leave it unticked). Else there will be one blueprint scene generated per object selected.
- Draw all edge : mark all edges as freestyle on the mesh and activate edge mark on all view
- Background: set a world sky (blueprint style), else leave transparent background
- Render at finish: render directly the generated scene(s) (exported correctly named in a "Blueprint" subfolder at blend's file root location)

### Where ?
add the panel in the 3D view toolbar > create

### Demo
from this object:  
![panel](https://github.com/Pullusb/images_repo/raw/master/Blender_AutoBlueprint_panel.png)

4 view shows layout  
![4views](https://github.com/Pullusb/images_repo/raw/master/plane_BP_4Views.png)

3 views aligned  
![3views](https://github.com/Pullusb/images_repo/raw/master/plane_BP_3Views.png)


important note, the blueprint is done in another scene (your original scene and object are leaved untouched)  
![scene](https://github.com/Pullusb/images_repo/raw/master/Blender_AutoBlueprint_scenes.png)

The generated blueprint might not be perfect, but it'll be a good start and will be easily tweakable trough well prepared freestyle  line set  
![tweaking](https://github.com/Pullusb/images_repo/raw/master/Blender_AutoBlueprint_settings.png)

--------
**/!\ Unstable, may crash blender**
The script usually Works, but many problems to patch and sometimes crashes (if so you may want to reopen and retry).
It was develloped as an exercise and a hobby, don't have time to work on it anymore.
So be sure to save your scene before launching ;)
