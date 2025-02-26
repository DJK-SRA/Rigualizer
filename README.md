# INSTALLATION:
This is a one-file plugin for Blender, meaning all you need to run Rigualizer is a single Python file. Simply:
1. Copy the raw contents of "rigualizer.py".
2. Go into Blender's "Scripting" tab.
3. Click "+New" to create a new text block.
4. Paste the contents of "rigualizer.py" into the Text Editor.
5. Run the script by Clicking ▶️ or using the shortcut Alt+P.
![rigualizerguide](https://github.com/user-attachments/assets/c68a6eae-312f-4aaa-bb0f-db0465231d1e)

And just like that, you've installed Rigualizer!
(Note that you'll need to re-run this script every time you re-launch Blender in order to access the sidebar. There are ways to automate this, but ~~I didn't feel like talking about it, plus I don't quite know~~ doing so is trivial and left as an exercise for the reader.

# GETTING STARTED: 
Now that you've installed Rigualizer, check for a new tab in your sidebar labeled "Misc". If you can click on it and you see the following panel, you'll know you've installed the plugin properly.
![image](https://github.com/user-attachments/assets/3ae900e5-63f0-4dab-842b-2c6797460da5)
NOTE: Before you use Rigualizer, make sure you've properly set up your desired framerate in-project. A visualizer's playback speed is currently tied to framerate.
To create a basic visualizer rig using the plugin, follow these instructions: 
1. Provide the audio file you wish to use in the "File Path" dialog.
  - If you wish to hear the audio file alongside the visualizer, check the "Add Audio" box before Step 2.
  - By default, Rigualizer will generate a 10-band visualizer. If you wish for more or less detail with your rig, change the "Band Amount" before Step 2.
2. Click "Sound Visualizer". (Note that the program may freeze for a few seconds during armature generation.)

Just like that, you've got a simple, music-driven armature which you can connect to a model however you wish! The horizontal row of bones you'll see are the frequency bands that move in time with the music, and the one bone centered below is the root bone to which all frequency bands are parented.
(Please note that currently, Rigualizer does not provide any models. The end user is currently expected to create their own model and parent it to the generated rig.) 

## RE-USING YOUR VISUALIZER WITH DIFFERNT AUDIO: 
A convenient element of Rigualizer is that it saves the generated rig movement to a Blender Action. This means you can create a rig once and re-use your rig with different audio files, rather than needing to create a new rig every time you wish to change the audio.
To add a different audio file to your generated rig, follow these instructions:
1. Select your current rig.
2. Check the "Use Active" box in the panel.
3. Provide the new audio file you wish to use in the "File Path" dialog.
   - If you wish to hear the audio file alongside the visualizer, check the "Add Audio" box before Step 4.
4. Click "Sound Visualizer". (Note that the program may freeze for a few seconds during audio re-binding.)

Now, if you play your scene, you should notice your rig moving in time with the new audio you provided.

If you ever wish to go back to an audio file you've previously provided, follow these instructions:
1. Select your current rig.
2. Use the "Selected Action" dropdown to select the file name corresponding to the audio you wish to use.
3. Click "Action and Sound Selector".

And now, you should be back to the previous audio you've selected!


# SPECIAL THANKS: 
- doakey3. Their plugin Bisualizer is excellent for quick and easy Visualizer generation, and whose code is a helpful template for this project.
- Jango-Blender, for their many contributions to the Rigualizer source code.
- Dude Blender, whose Blender visualizer tutorial helped lay the groundworks for the plugin.
- The kind members of the Blender Community Discord.
