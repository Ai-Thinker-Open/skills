# Vorbis Audio Codec API Reference

## Overview

Vorbis is an open-source lossy audio codec developed by Xiph.Org, similar to MP3 but using more advanced compression algorithms. Vorbis audio is typically encapsulated in the OGG container (also known as OggVorbis) and is widely used in gaming, music streaming, and network audio transmission. On the BL618 chip platform, the Vorbis decoding library can be used to implement music playback functionality, supporting decoding and playback of OGG/Vorbis audio from filesystems or streaming sources.

## Key Data Types

### OggVorbis_File

OggVorbis_File is the most important file handle structure, used to manage the complete state of an OGG/Vorbis file:

```c
typedef struct OggVorbis_File {
  void            *datasource;   // Data source pointer (FILE* or custom)
  int              seekable;     // Whether seek is supported
  ogg_int64_t      offset;       // Current file offset
  ogg_int64_t      end;          // File end position
  ogg_sync_state   oy;           // OGG sync state
  int              links;        // Number of logical streams
  ogg_int64_t     *offsets;      // Stream offset table
  ogg_int64_t     *dataoffsets;  // Data offset per stream
  long            *serialnos;    // Serial number list
  ogg_int64_t     *pcmlengths;   // Total PCM sample count
  vorbis_info     *vi;           // Audio stream information
  vorbis_comment  *vc;           // User comment information
  ogg_int64_t      pcm_offset;   // Current PCM position
  int              ready_state;  // Ready state
  long             current_serialno;
  int              current_link;
  double           bittrack;
  double           samptrack;
  ogg_stream_state os;           // OGG stream state
  vorbis_dsp_state vd;           // DSP decoding state
  vorbis_block     vb;           // Audio block workspace
  ov_callbacks     callbacks;    // Callback function set
} OggVorbis_File;
```

### vorbis_info

vorbis_info stores basic configuration information of the audio stream:

```c
typedef struct vorbis_info{
  int version;           // Vorbis version
  int channels;          // Number of channels (1=mono, 2=stereo)
  long rate;             // Sampling rate (Hz)
  long bitrate_upper;    // Upper bitrate
  long bitrate_nominal;  // Nominal bitrate
  long bitrate_lower;    // Lower bitrate
  long bitrate_window;   // Bitrate window
  void *codec_setup;     // Codec internal configuration
} vorbis_info;
```

### vorbis_comment

vorbis_comment stores metadata comments for audio files (similar to ID3 tags):

```c
typedef struct vorbis_comment{
  char **user_comments;    // Comment array
  int   *comment_lengths;  // Length of each comment
  int    comments;         // Number of comments
  char  *vendor;           // Encoder vendor string
} vorbis_comment;
```

### ov_callbacks

ov_callbacks defines the callback function set for file operations, compatible with the stdio interface:

```c
typedef struct {
  size_t (*read_func)  (void *ptr, size_t size, size_t nmemb, void *datasource);
  int    (*seek_func)  (void *datasource, ogg_int64_t offset, int whence);
  int    (*close_func) (void *datasource);
  long   (*tell_func)  (void *datasource);
} ov_callbacks;
```

Predefined callback sets:
- `OV_CALLBACKS_DEFAULT`: Standard file operations (seekable/closeable)
- `OV_CALLBACKS_NOCLOSE`: Does not close the data source
- `OV_CALLBACKS_STREAMONLY`: Stream mode (non-seekable)
- `OV_CALLBACKS_STREAMONLY_NOCLOSE`: Stream mode and does not close

### Opaque Structures

The following structures are opaque types, operated only through API functions:

- **vorbis_dsp_state**: DSP state structure, buffering current audio analysis/synthesis state
- **vorbis_block**: Audio block structure, a single audio data block pending processing

## Core API

### File Open and Close

#### ov_open_callbacks()

```c
int ov_open_callbacks(void *datasource, OggVorbis_File *vf,
                      const char *initial, long ibytes, ov_callbacks callbacks);
```

Opens an OGG/Vorbis file through custom callback functions. datasource can be FILE* or other custom data sources. initial and ibytes are used to skip the file header (typically pass NULL and 0). Returns 0 on success.

#### ov_fopen()

```c
int ov_fopen(const char *path, OggVorbis_File *vf);
```

Convenience function that opens a file directly by file path, using standard file operation callbacks internally.

#### ov_test_callbacks() / ov_test()

```c
int ov_test_callbacks(void *datasource, OggVorbis_File *vf,
                     const char *initial, long ibytes, ov_callbacks callbacks);
int ov_test(FILE *f, OggVorbis_File *vf, const char *initial, long ibytes);
```

Test mode, parses only the file header without initializing the full decoder. Requires subsequent call to `ov_test_open()` to complete initialization. Suitable for scenarios where audio format detection is needed while downloading.

#### ov_open1() / ov_open2()

```c
int ov_open1(OggVorbis_File *vf);
int ov_open2(OggVorbis_File *vf);
```

Step-by-step initialization interfaces. `ov_open1()` parses the file header, `ov_open2()` completes decoder initialization. Used for scenarios requiring fine-grained control over the initialization process.

#### ov_clear()

```c
int ov_clear(OggVorbis_File *vf);
```

Closes an opened Vorbis file and releases all associated resources. Must be called after using the file.

### Audio Decoding

#### ov_read()

```c
long ov_read(OggVorbis_File *vf, char *buffer, int length,
             int bigendianp, int word, int sgned, int *bitstream);
```

Decodes and returns the next frame of PCM data. Parameter descriptions:
- buffer: output buffer
- length: buffer length (bytes)
- bigendianp: endianness (0=little-endian)
- word: sample width (1=8bit, 2=16bit, 3=24bit, 4=32bit)
- sgned: whether signed (0=unsigned, 1=signed)
- bitstream: outputs the current bitstream index

Returns the number of bytes read, 0 indicates end of file, negative values indicate errors.

#### ov_read_float()

```c
long ov_read_float(OggVorbis_File *vf, float ***pcm_channels, int samples,
                   int *bitstream);
```

Decodes and returns PCM data in floating-point format. pcm_channels is a pointer array to multi-channel float buffers, samples specifies the number of samples per channel. Returns the actual number of samples read.

### File Information Query

#### ov_pcm_total() / ov_time_total()

```c
ogg_int64_t ov_pcm_total(OggVorbis_File *vf, int i);
double ov_time_total(OggVorbis_File *vf, int i);
```

Get the total duration of the audio. i is the logical stream index (-1 means current stream). `ov_pcm_total()` returns the total PCM sample count, `ov_time_total()` returns the duration in seconds.

#### ov_info()

```c
vorbis_info *ov_info(OggVorbis_File *vf, int link);
```

Gets the vorbis_info for the specified stream, including sampling rate, number of channels, and bitrate.

#### ov_comment()

```c
vorbis_comment *ov_comment(OggVorbis_File *vf, int link);
```

Gets the vorbis_comment for the specified stream, including metadata such as artist and album.

### Seeking

#### ov_pcm_seek()

```c
int ov_pcm_seek(OggVorbis_File *vf, ogg_int64_t pos);
```

Seeks to the specified PCM sample position. pos is the PCM sample offset from the beginning of the file.

#### ov_time_seek()

```c
int ov_time_seek(OggVorbis_File *vf, double pos);
```

Seeks to the specified time position. pos is the playback time in seconds.

### Low-Level Synthesis API

The following are low-level APIs for the Vorbis synthesis layer:

#### vorbis_synthesis_init()

```c
int vorbis_synthesis_init(vorbis_dsp_state *v, vorbis_info *vi);
```

Initializes the DSP synthesizer, applying the vorbis_info configuration to the dsp_state.

#### vorbis_block_init()

```c
int vorbis_block_init(vorbis_dsp_state *v, vorbis_block *vb);
```

Initializes a vorbis_block audio block, associating it with the specified dsp_state.

#### vorbis_synthesis()

```c
int vorbis_synthesis(vorbis_block *vb, ogg_packet *op);
```

Decodes an OGG data packet into PCM samples in the block. The decoded PCM is extracted via `vorbis_synthesis_pcmout()`.

## Error Codes

Vorbis API returns negative values to indicate errors:
- `OV_FALSE`: General failure
- `OV_EOF`: End of file
- `OV_HOLE`: Data loss
- `OV_EREAD`: Read error
- `OV_EFAULT`: Internal error
- `OV_EINVAL`: Invalid parameter
- `OV_ENOTVORBIS`: Not a Vorbis file
- `OV_EBADHEADER`: Corrupted file header
- `OV_EVERSION`: Unsupported Vorbis version
- `OV_ENOSEEK`: Stream is not seekable

## Code Examples

The following example demonstrates how to use the Vorbis API to open an OGG file and decode it for playback:

```c
#include <vorbis/vorbisfile.h>
#include <stdio.h>

#define PCM_BUFFER_SIZE 4096

int play_vorbis_file(const char *filename)
{
    OggVorbis_File vf;
    FILE *fp;
    char buffer[PCM_BUFFER_SIZE];
    int  bitstream;
    long bytes_read;
    vorbis_info *vi;

    /* Open file */
    if (ov_fopen(filename, &vf) != 0) {
        printf("Failed to open file: %s\n", filename);
        return -1;
    }

    /* Get audio stream information */
    vi = ov_info(&vf, -1);
    printf("Channels: %d, Rate: %ld Hz\n", vi->channels, vi->rate);

    /* Loop read and decode */
    while ((bytes_read = ov_read(&vf, buffer, sizeof(buffer),
                                  0, 2, 1, &bitstream)) > 0) {
        /* Feed PCM data to audio output
         * Platform-specific audio playback API can be called here
         */
        // audio_write(buffer, bytes_read);
    }

    /* Close file */
    ov_clear(&vf);
    return 0;
}
```

Example using floating-point format decoding:

```c
int play_vorbis_float(const char *filename)
{
    OggVorbis_File vf;
    float **pcm_channels;
    long samples;
    int  bitstream, i, ch;

    if (ov_fopen(filename, &vf) != 0) {
        return -1;
    }

    while ((samples = ov_read_float(&vf, &pcm_channels, 4096, &bitstream)) > 0) {
        vorbis_info *vi = ov_info(&vf, -1);
        int channels = vi->channels;

        /* Process multi-channel data
         * pcm_channels[0] is left channel
         * pcm_channels[1] is right channel
         * and so on
         */
        for (ch = 0; ch < channels; ch++) {
            for (i = 0; i < samples; i++) {
                float sample = pcm_channels[ch][i];
                /* process sample... */
            }
        }
    }

    ov_clear(&vf);
    return 0;
}
```

## References

- Xiph.Org Foundation: https://xiph.org/vorbis/
- Vorbis Official Documentation: https://xiph.org/vorbis/doc/
- OGG Container Format Specification: https://xiph.org/ogg/doc/
