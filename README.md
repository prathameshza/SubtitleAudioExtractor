# SubtitleAudioExtractor
A streamlit program to extract audio clips from the subtitle files for the purpose of TTS and other data science related projects

## Usage
In order to use the streamlit interface do the following tasks

Download and open this folder in a terminal or a code editor and type

```
pip install -r requirements.txt
```
*Installing Requirements (Only once)*

```
streamlit run sae.py 
```
*Launching the app on localhost*

## Interface
Initial interface will look like this
![sae_interface](https://github.com/prathameshza/SubtitleAudioExtractor/assets/46810093/8d6785dc-fc5c-46af-9409-50904416897d)

After adding the audio and srt files of your choice (we used the files from sample_files folder below)
![sae](https://github.com/prathameshza/SubtitleAudioExtractor/assets/46810093/59446039-0ee1-4f83-953b-29e253851100)

After the process is complete you will have a folder of audio_directory and subtitle_directory containing srt segments of the audio and txt files.
This app will also create 2 csv files ttsdata and ttsdata2 which is shown in the above figure.
>Note: This sample_files are for Hindi language but it should support any language
