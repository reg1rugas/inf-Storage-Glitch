## Infinite Storage Glitch (Youtube)
theoretically store infinite files encoded as videos on Youtube; practically get your account banned for misconduct


## How to use:
install prerequisites using pip 

```python
pip install -r requirements.txt
```

And then simply use converter.py for operations
```bash
python converter.py -h
```
<img width="600" height="346" alt="image" src="https://github.com/user-attachments/assets/75f9c47f-9c49-4d08-ac4a-18e040b018a7" />

### Example

start with encoding your file (any filetype) into a video
```bash
# Encode
python converter.py --file demo.zip
```
<img src="https://github.com/user-attachments/assets/a7c32813-b464-42a6-91bd-1b808e98e8a4" width="500" height="250"/>

then upload the generated video to your youtube channel and download it back for retrieval by

```bash
# Download
python converter.py --download https://www.youtube.com/watch?v=q0MEYLTetYA
```

finally decode 

```bash
# Decode
python converter.py --video downloaded_video.mkv
```


## How It Works

1. **Encoding (File → Video)**
   - The file is read in binary (`0` and `1` bits).
   - Each bit is represented as a pixel block:
     - `1` → black
     - `0` → white
   - Frames are generated from these pixels to form a video.
   - To avoid loss of data via YT compression algorithm pixel blocks are used instead of singular pixels (set by PIXEL_SIZE)

2. **Decoding (Video → File)**
   - Each frame is read pixel_block-by-pixel_block.
   - Pixels are converted back into bits using brightness thresholds.
   - Bits are grouped into bytes and written back to reconstruct the file.
