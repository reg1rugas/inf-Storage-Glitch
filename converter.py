import argparse
import io
import numpy as np
from tqdm import tqdm
import imageio
import filetype
from PIL import Image
from moviepy import ImageSequenceClip
from PIL import Image
from moviepy import ImageSequenceClip
import yt_dlp


WIDTH=1920
HEIGHT=1080
PIXEL_SIZE=4
FPS=30              # test before changing as imageio has a bug that skips the last frame due to faulty float arithmetic. See https://github.com/zulko/moviepy/issues/2507

def file_to_video(path, width=WIDTH, height=HEIGHT, pixel_size=PIXEL_SIZE, fps=FPS):
    try:
        binary_data = ""
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024), b""):
                binary_data += "".join(f"{byte:08b}" for byte in chunk)

        total_pixels = len(binary_data) #Number of pixels in total
        pixel_blocks = (width // pixel_size) * (height // pixel_size) #Image downsampling, pixelation grids
        n_image = (total_pixels + pixel_blocks - 1) // pixel_blocks  #Round up (total / pixel)

        frames = []
        print("No. of frames needed : ", n_image)


        for i in tqdm(range(n_image)):

            start_index = i * pixel_blocks   # get position wrt binary_data stream
            end_index = min(start_index + pixel_blocks, total_pixels) # where to end

            binary_digits = binary_data[start_index:end_index]

            if len(binary_digits) < pixel_blocks:                           # if frame incomplete pad w 0
                binary_digits = binary_digits.ljust(pixel_blocks, '0')

            img = Image.new('RGB', (width, height), color='white')  # 1 new frame

            for row_index in range(height // pixel_size): 

                start_index = row_index * (width // pixel_size)
                end_index = start_index + (width // pixel_size)
                row = binary_digits[start_index:end_index]

                for c_index, val in enumerate(row):
                    if val == '1':
                        color = (0, 0, 0)  # Black
                    else:
                        color = (255, 255, 255)  # White

                    # coordinates of the pixel block
                    x1 = c_index * pixel_size
                    y1 = row_index * pixel_size
                    x2 = x1 + pixel_size
                    y2 = y1 + pixel_size

                    # Draw the pixel on the image
                    img.paste(color, (x1, y1, x2, y2))

            with io.BytesIO() as f:
                img.save(f, format='PNG')
                frame = np.array(Image.open(f))   #save frame
            frames.append(frame)

        clip = ImageSequenceClip(frames, fps=fps)
        clip.write_videofile('video.mp4')

    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")


def video_to_file(path, width=WIDTH, height=HEIGHT, pixel_size=PIXEL_SIZE):
    try:
        vid = imageio.get_reader(path, 'ffmpeg')
        frames = []
        num_frames = vid.get_length()

        with tqdm(total=num_frames) as pbar:
            # Iterate over every frame of the video
            for i, frame in enumerate(vid):

                frames.append(frame)
                pbar.update(1) # Update the progress bar


        threshold = 128   # pixels darker than 128 are considered 1 

        binary_digits = ''

        for frame in tqdm(frames, desc="Processing frames"):
            gray_frame = np.mean(frame, axis=2).astype(np.uint8)  # Convert the frame to grayscale

            pixel_size = PIXEL_SIZE

            for y in range(0, gray_frame.shape[0], pixel_size):  #row
                for x in range(0, gray_frame.shape[1], pixel_size): #coloumn

                    color = gray_frame[y:y+pixel_size, x:x+pixel_size]

                    if color.mean() < threshold:
                        binary_digits += '1'
                    else:
                        binary_digits += '0'

        if len(binary_digits) % 8 != 0:
            binary_digits = binary_digits.ljust(((len(binary_digits) + 7) // 8) * 8, '0')

        binary_data = bytes(int(binary_digits[i:i+8], 2) for i in range(0, len(binary_digits), 8))

        l = filetype.guess(binary_data).mime
        ext = l.split(sep='/')[-1]

        with open(f'result.{ext}', 'wb') as f:   # incase of zip it is saved as .octet-stream due to python-magic being dumb
            for chunk in range(0, len(binary_data), 1024):        
                f.write(binary_data[chunk:chunk+1024])


    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def download_video(url, output_path="."):
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]/bestvideo',    # pick best video stream only (no audio, no merging)
        'merge_output_format': None,
        'postprocessors': [],
        'quiet': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog='converter')
    parser.add_argument('-f', '--file', help="Convert file to video")  
    parser.add_argument('-v', '--video', help="Convert video to file")  
    parser.add_argument('-d', '--download', help="Download YT video from link")  
    args = parser.parse_args()

    if not (args.file or args.video or args.download):
        parser.error("Missing arguements :(")

    if args.file:
        file_to_video(args.file)
    elif args.video:
        video_to_file(args.video)
    else:
        download_video(args.download)  #Sample : https://www.youtube.com/watch?v=q0MEYLTetYA

