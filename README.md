# Youtube Downloader
## _Download a youtube video or playlist in audio or video form_


## Features

- Download a full playlist or just a single video
- Download either audio or video
- Specify file extensions
- Zip files if required


## Tech

Youtube Downloader uses a number of open source projects to work properly:

- [YoutubeDL] - used to extract playlist data
- [Pafy] - used to download the video or audio for each video

## Installation

Youtube Downloader requires [Python 3](https://www.python.org/downloads//) v3.8+ to run.

Install the dependencies.

```sh
pip install -r (Path)\YoutubeVideoDownloader\requirements.txt
```

## Usage

  1. Copy a link to a youtube video or playlist.
    1a. Due to issues with Pafy, any videos that have comments or likes disabled are unable to be downloaded
  2. Paste this into the console once prompted.
  3. Enter 1 for video and 2 for only audio
  4. Specify required file extension from provided options
  5. Enter whether you want the files to be compressed into a zip file, or remain in a folder
  6. Your file(s) will download into the download folder in the program installation folder
    6a. The files will be stored in a folder with the current date and time as its name

## Example
- Copy URL
![image](https://user-images.githubusercontent.com/79090791/124382145-d5dea500-dcbd-11eb-9c3f-6e6f975f3a8c.png)
- Paste into console and fill in options as required
![image](https://user-images.githubusercontent.com/79090791/124382312-a4b2a480-dcbe-11eb-8eb3-f46a94791d31.png)
- See result
![image](https://user-images.githubusercontent.com/79090791/124382371-feb36a00-dcbe-11eb-91c5-886d494630bf.png)

## License

MIT

**Free to use however you want!**


   [YoutubeDL]: <https://github.com/ytdl-org/youtube-dl>
   [SimpleHTR]: <https://github.com/githubharald/SimpleHTR>
   

