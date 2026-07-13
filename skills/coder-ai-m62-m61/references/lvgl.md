# LVGL Graphics Library Documentation (v9)

This document covers LVGL v9 integration on Bouffalo Lab BL616/BL618 platforms using the Bouffalo SDK.

## Table of Contents
- [Initialization](#initialization)
- [Display Driver](#display-driver)
- [Input Driver](#input-driver)
- [Object System](#object-system)
- [Button Widget](#button-widget)
- [Label Widget](#label-widget)
- [Image Widget](#image-widget)
- [Timer System](#timer-system)
- [Working Example](#working-example)

---

## Initialization

### `lv_init()`

Initialize the LVGL library. Must be called before any other LVGL functions.

```c
#include "lvgl.h"

void lv_init(void);
```

**Example:**
```c
int main(void)
{
    // Hardware init (SPI, GPIO, etc.)
    hardware_init();

    // Initialize LVGL
    lv_init();

    // Setup display and input drivers
    my_display_init();
    my_input_init();

    // Create UI
    create_ui();

    // Main loop
    while (1) {
        lv_timer_handler_run_in_period(5);  // Run every 5ms
        delay_ms(5);
    }
}
```

### `lv_deinit()`

Deinitialize the LVGL library.

```c
void lv_deinit(void);
```

### `lv_is_initialized()`

Check if LVGL is initialized.

```c
bool lv_is_initialized(void);
```

---

## Display Driver

### Display Creation

Create a display with specified resolution:

```c
lv_display_t * lv_display_create(int32_t hor_res, int32_t ver_res);
```

### Display Configuration

```c
// Set default display
void lv_display_set_default(lv_display_t * disp);

// Set flush callback (called when framebuffer is ready to send to display)
void lv_display_set_flush_cb(lv_display_t * disp, lv_display_flush_cb_t flush_cb);

// Set draw buffers
// render_mode: LV_DISPLAY_RENDER_MODE_PARTIAL, DIRECT, or FULL
void lv_display_set_buffers(lv_display_t * disp, void * buf1, void * buf2, 
                           uint32_t buf_size, lv_display_render_mode_t render_mode);

// Set color format
void lv_display_set_color_format(lv_display_t * disp, lv_color_format_t color_format);
```

### Flush Callback

The flush callback is invoked when LVGL has rendered content to the buffer:

```c
void my_flush_callback(lv_display_t * disp, const lv_area_t * area, uint8_t * px_map)
{
    // area: region that needs to be updated
    // px_map: pointer to pixel data (RGB565 format typically)
    
    // Copy to display hardware (SPI, RGB interface, etc.)
    display_send_pixels(area->x1, area->y1, area->x2, area->y2, px_map);
    
    // Notify LVGL that flushing is complete
    lv_display_flush_ready(disp);
}
```

### Display Rotation

```c
void lv_display_set_rotation(lv_display_t * disp, lv_display_rotation_t rotation);
// Options: LV_DISPLAY_ROTATION_0, _90, _180, _270
```

---

## Input Driver

### Input Device Types

```c
typedef enum {
    LV_INDEV_TYPE_NONE,      // Uninitialized
    LV_INDEV_TYPE_POINTER,   // Touch pad, mouse
    LV_INDEV_TYPE_KEYPAD,    // Keyboard
    LV_INDEV_TYPE_BUTTON,    // Hardware buttons
    LV_INDEV_TYPE_ENCODER,   // Rotary encoder
} lv_indev_type_t;
```

### Input Device Creation

```c
lv_indev_t * lv_indev_create(void);
```

### Input Device Configuration

```c
// Set input device type
void lv_indev_set_type(lv_indev_t * indev, lv_indev_type_t indev_type);

// Set read callback (polls input hardware)
void lv_indev_set_read_cb(lv_indev_t * indev, lv_indev_read_cb_t read_cb);

// Assign display to input device
void lv_indev_set_display(lv_indev_t * indev, lv_display_t * disp);

// Set long press time (ms)
void lv_indev_set_long_press_time(lv_indev_t * indev, uint16_t time);

// Enable/disable input device
void lv_indev_enable(lv_indev_t * indev, bool enable);
```

### Read Callback for Touch

```c
void my_touch_read_cb(lv_indev_t * indev, lv_indev_data_t * data)
{
    // Read touch coordinates from touch controller
    int x, y;
    bool pressed = touch_get_point(&x, &y);
    
    data->point.x = x;
    data->point.y = y;
    data->state = pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}
```

### Read Callback for Buttons

```c
void my_button_read_cb(lv_indev_t * indev, lv_indev_data_t * data)
{
    // Read button state
    static uint32_t last_btn = 0;
    
    uint32_t btn = button_read();  // Returns button ID (0, 1, 2, ...)
    
    data->btn_id = btn;
    data->state = (btn != 0) ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
    
    last_btn = btn;
}

// Set button points (maps buttons to screen coordinates)
lv_point_t btn_points[] = {{20, 60}, {60, 60}, {100, 60}};
lv_indev_set_button_points(indev, btn_points);
```

---

## Object System

### `lv_obj_create()`

Create a base object (rectangle). All widgets inherit from this.

```c
lv_obj_t * lv_obj_create(lv_obj_t * parent);
```

**Parameters:**
- `parent`: Parent object (or `NULL` for screen)

**Returns:** Pointer to created object

### Common Object Functions

```c
// Position and size
void lv_obj_set_pos(lv_obj_t * obj, int32_t x, int32_t y);
void lv_obj_set_size(lv_obj_t * obj, int32_t w, int32_t h);
void lv_obj_set_x(lv_obj_t * obj, int32_t x);
void lv_obj_set_y(lv_obj_t * obj, int32_t y);

// Alignment
void lv_obj_align(lv_obj_t * obj, lv_align_t align, int32_t x_ofs, int32_t y_ofs);
// align: LV_ALIGN_CENTER, LV_ALIGN_TOP_MID, LV_ALIGN_BOTTOM_LEFT, etc.

// Flags
void lv_obj_add_flag(lv_obj_t * obj, lv_obj_flag_t flag);
void lv_obj_remove_flag(lv_obj_t * obj, lv_obj_flag_t flag);
// Flags: LV_OBJ_FLAG_HIDDEN, LV_OBJ_FLAG_CLICKABLE, LV_OBJ_FLAG_SCROLLABLE, etc.

// Delete
void lv_obj_delete(lv_obj_t * obj);
```

---

## Button Widget

### `lv_button_create()`

```c
lv_obj_t * lv_button_create(lv_obj_t * parent);
```

**Example:**
```c
// Create screen
lv_obj_t * screen = lv_screen_active();

// Create button
lv_obj_t * btn = lv_button_create(screen);
lv_obj_set_size(btn, 120, 50);
lv_obj_align(btn, LV_ALIGN_CENTER, 0, 0);

// Add label to button
lv_obj_t * label = lv_label_create(btn);
lv_label_set_text(label, "Click Me");
lv_obj_center(label);

// Set click event
lv_obj_add_event_cb(btn, btn_event_cb, LV_EVENT_CLICKED, NULL);

// Event callback
void btn_event_cb(lv_event_t * e)
{
    LV_LOG_USER("Button clicked!");
}
```

### Button Styles

```c
// Set button style
static lv_style_t style_btn;
lv_style_init(&style_btn);
lv_style_set_bg_color(&style_btn, lv_color_hex(0x4CAF50));
lv_style_set_radius(&style_btn, 10);
lv_obj_add_style(btn, &style_btn, LV_PART_MAIN);
```

---

## Label Widget

### `lv_label_create()`

```c
lv_obj_t * lv_label_create(lv_obj_t * parent);
```

### Text Functions

```c
// Set text (allocates memory)
void lv_label_set_text(lv_obj_t * obj, const char * text);

// Set formatted text (like printf)
void lv_label_set_text_fmt(lv_obj_t * obj, const char * fmt, ...);

// Set static text (doesn't allocate - text must persist)
void lv_label_set_text_static(lv_obj_t * obj, const char * text);

// Get text
char * lv_label_get_text(const lv_obj_t * obj);
```

### Long Mode (Text Overflow Behavior)

```c
void lv_label_set_long_mode(lv_obj_t * obj, lv_label_long_mode_t long_mode);
// Options:
//   LV_LABEL_LONG_MODE_WRAP           - Wrap to next line, expand height
//   LV_LABEL_LONG_MODE_DOTS           - Show "..." at end
//   LV_LABEL_LONG_MODE_SCROLL         - Scroll back and forth
//   LV_LABEL_LONG_MODE_SCROLL_CIRCULAR - Continuous scroll
//   LV_LABEL_LONG_MODE_CLIP           - Clip at boundary
```

### Other Functions

```c
// Enable recoloring (parse #FF0000 red# in text)
void lv_label_set_recolor(lv_obj_t * obj, true);

// Set text selection
void lv_label_set_text_selection_start(lv_obj_t * obj, uint32_t index);
void lv_label_set_text_selection_end(lv_obj_t * obj, uint32_t index);
```

**Example:**
```c
lv_obj_t * label = lv_label_create(screen);
lv_label_set_text(label, "Hello World");
lv_obj_set_pos(label, 10, 10);

// With colored text
lv_label_set_recolor(label, true);
lv_label_set_text(label, "#FF0000 Red# and #00FF00 Green# text");

// With long text and dots
lv_obj_set_size(label, 100, 20);
lv_label_set_long_mode(label, LV_LABEL_LONG_MODE_DOTS);
lv_label_set_text(label, "This is a very long text...");
```

---

## Image Widget

### `lv_image_create()`

```c
lv_obj_t * lv_image_create(lv_obj_t * parent);
```

### Source Functions

```c
// Set image source
void lv_image_set_src(lv_obj_t * obj, const void * src);
// src can be:
//   - lv_image_dsc_t pointer (C array from image converter)
//   - File path: "S:/dir/image.bin"
//   - Symbol: LV_SYMBOL_OK

// Declare image from C array (use LVGL image converter)
LV_IMAGE_DECLARE(my_image);
lv_image_set_src(img, &my_image);

// Get source
const void * lv_image_get_src(const lv_obj_t * obj);
```

### Transformations

```c
// Scale (256 = 100%, 128 = 50%, 512 = 200%)
void lv_image_set_scale(lv_obj_t * obj, uint32_t zoom);
void lv_image_set_scale_x(lv_obj_t * obj, uint32_t zoom);
void lv_image_set_scale_y(lv_obj_t * obj, uint32_t zoom);

// Rotation (0-3600 = 0-360 degrees, in 0.1 degree increments)
void lv_image_set_rotation(lv_obj_t * obj, int32_t angle);

// Rotation pivot (center point)
void lv_image_set_pivot(lv_obj_t * obj, int32_t x, int32_t y);

// Offset (for tiled images)
void lv_image_set_offset_x(lv_obj_t * obj, int32_t x);
void lv_image_set_offset_y(lv_obj_t * obj, int32_t y);
```

### Alignment Mode

```c
void lv_image_set_inner_align(lv_obj_t * obj, lv_image_align_t align);
// Options:
//   LV_IMAGE_ALIGN_CENTER
//   LV_IMAGE_ALIGN_TOP_LEFT, TOP_MID, TOP_RIGHT
//   LV_IMAGE_ALIGN_BOTTOM_LEFT, BOTTOM_MID, BOTTOM_RIGHT
//   LV_IMAGE_ALIGN_LEFT_MID, RIGHT_MID
//   LV_IMAGE_ALIGN_STRETCH    - Fill widget area
//   LV_IMAGE_ALIGN_COVER     - Fill while keeping aspect ratio
//   LV_IMAGE_ALIGN_CONTAIN   - Fit inside while keeping aspect ratio
```

**Example:**
```c
lv_obj_t * img = lv_image_create(screen);
lv_obj_set_size(img, 100, 100);
lv_obj_align(img, LV_ALIGN_CENTER, 0, 0);

// Set image
LV_IMAGE_DECLARE(my_icon);
lv_image_set_src(img, &my_icon);

// Apply transformations
lv_image_set_scale(img, 256);        // 100%
lv_image_set_rotation(img, 900);      // 90 degrees
lv_image_set_pivot(img, 50, 50);     // Rotate around center
```

---

## Timer System

### `lv_timer_create()`

Create a periodic timer.

```c
lv_timer_t * lv_timer_create(lv_timer_cb_t timer_xcb, uint32_t period, void * user_data);
```

**Parameters:**
- `timer_xcb`: Callback function called periodically
- `period`: Period in milliseconds
- `user_data`: Custom data passed to callback

### Timer Functions

```c
// Delete timer
void lv_timer_delete(lv_timer_t * timer);

// Pause/Resume
void lv_timer_pause(lv_timer_t * timer);
void lv_timer_resume(lv_timer_t * timer);

// Modify timer
void lv_timer_set_period(lv_timer_t * timer, uint32_t period);
void lv_timer_set_cb(lv_timer_t * timer, lv_timer_cb_t timer_cb);
void lv_timer_set_user_data(lv_timer_t * timer, void * user_data);

// Reset (restart from now)
void lv_timer_reset(lv_timer_t * timer);

// Make timer ready (execute on next handler call)
void lv_timer_ready(lv_timer_t * timer);

// Set repeat count (-1 = infinite, 0 = stop, n = repeat n times)
void lv_timer_set_repeat_count(lv_timer_t * timer, int32_t repeat_count);

// Auto delete when repeat_count reaches 0
void lv_timer_set_auto_delete(lv_timer_t * timer, bool auto_delete);
```

### Timer Handler

```c
// Run timer handler (call in main loop)
uint32_t lv_timer_handler_run_in_period(uint32_t period);

// Or use periodic handler directly
void lv_timer_periodic_handler(void);
```

### Timer Callback

```c
void my_timer_callback(lv_timer_t * timer)
{
    // Access user data
    my_data_t * data = (my_data_t *) lv_timer_get_user_data(timer);
    
    // Do work
    update_something();
    
    LV_LOG_TRACE("Timer callback");
}
```

**Example:**
```c
static uint32_t counter = 0;

void counter_timer_cb(lv_timer_t * timer)
{
    counter++;
    LV_LOG_USER("Counter: %" LV_PRId32, counter);
}

// Create timer - runs every 1000ms
lv_timer_t * timer = lv_timer_create(counter_timer_cb, 1000, NULL);

// Later, change period
lv_timer_set_period(timer, 500);  // Now every 500ms

// Pause timer
lv_timer_pause(timer);

// Resume timer
lv_timer_resume(timer);

// Delete timer
lv_timer_delete(timer);
```

---

## Working Example

Complete example showing display, touch input, button, label, image, and timer:

```c
#include "lvgl.h"

// Display buffer (adjust size based on available RAM)
static uint8_t disp_buf1[320 * 240 * 2];  // 320x240 RGB565
static uint8_t disp_buf2[320 * 240 * 2];

static lv_display_t * disp;
static lv_obj_t * label;
static uint32_t timer_counter = 0;

// Display flush callback
void my_flush_cb(lv_display_t * disp, const lv_area_t * area, uint8_t * px_map)
{
    // Send pixels to display hardware
    // Example for SPI display:
    // ili9341_draw_bitmap(area->x1, area->y1, area->x2, area->y2, px_map);
    
    // For simulation, just mark complete
    lv_display_flush_ready(disp);
}

// Touch read callback
void my_touch_cb(lv_indev_t * indev, lv_indev_data_t * data)
{
    // Read from touch controller
    int x, y;
    bool pressed = touch_get_position(&x, &y);
    
    data->point.x = x;
    data->point.y = y;
    data->state = pressed ? LV_INDEV_STATE_PRESSED : LV_INDEV_STATE_RELEASED;
}

// Timer callback
void timer_callback(lv_timer_t * timer)
{
    timer_counter++;
    lv_label_set_text_fmt(label, "Count: %" LV_PRId32, timer_counter);
}

// Button event callback
void btn_event_cb(lv_event_t * e)
{
    lv_obj_t * btn = lv_event_get_target(e);
    LV_LOG_USER("Button pressed!");
    
    // Change label text on button press
    lv_label_set_text(label, "Button Clicked!");
}

void ui_init(void)
{
    // Create display
    disp = lv_display_create(320, 240);
    lv_display_set_buffers(disp, disp_buf1, disp_buf2, sizeof(disp_buf1),
                           LV_DISPLAY_RENDER_MODE_PARTIAL);
    lv_display_set_flush_cb(disp, my_flush_cb);
    lv_display_set_color_format(disp, LV_COLOR_FORMAT_RGB565);
    
    // Get active screen
    lv_obj_t * screen = lv_screen_active();
    
    // Create label
    label = lv_label_create(screen);
    lv_label_set_text(label, "Hello LVGL!");
    lv_obj_set_pos(label, 100, 30);
    
    // Create button with label
    lv_obj_t * btn = lv_button_create(screen);
    lv_obj_set_size(btn, 100, 40);
    lv_obj_align(btn, LV_ALIGN_CENTER, 0, 0);
    lv_obj_add_flag(btn, LV_OBJ_FLAG_CLICKABLE);
    lv_obj_add_event_cb(btn, btn_event_cb, LV_EVENT_CLICKED, NULL);
    
    lv_obj_t * btn_label = lv_label_create(btn);
    lv_label_set_text(btn_label, "Press Me");
    lv_obj_center(btn_label);
    
    // Create image (if you have image data)
    // LV_IMAGE_DECLARE(my_image);
    // lv_obj_t * img = lv_image_create(screen);
    // lv_image_set_src(img, &my_image);
    // lv_obj_align(img, LV_ALIGN_BOTTOM_MID, 0, -10);
}

void input_init(void)
{
    // Create touch input device
    lv_indev_t * indev = lv_indev_create();
    lv_indev_set_type(indev, LV_INDEV_TYPE_POINTER);
    lv_indev_set_read_cb(indev, my_touch_cb);
    lv_indev_set_display(indev, disp);
}

int main(void)
{
    // Hardware init
    // spi_init();
    // touch_init();
    
    // Initialize LVGL
    lv_init();
    
    // Initialize UI
    ui_init();
    
    // Initialize input
    input_init();
    
    // Create timer
    lv_timer_create(timer_callback, 1000, NULL);  // Every 1 second
    
    // Main loop
    while (1) {
        lv_timer_handler_run_in_period(5);  // Run every 5ms
        delay_ms(5);
    }
}
```

---

## Configuration (lv_conf.h)

Key settings in `lv_conf.h`:

```c
// Color depth
#define LV_COLOR_DEPTH 16           // RGB565

// Memory for LVGL
#define LV_MEM_SIZE (64 * 1024U)    // 64KB

// Display refresh period (ms)
#define LV_DEF_REFR_PERIOD  33      // ~30 FPS

// DPI setting
#define LV_DPI_DEF 130

// Enable widgets
#define LV_USE_BUTTON    1
#define LV_USE_LABEL     1
#define LV_USE_IMAGE     1
```

---

## Summary

| Component | Key Functions |
|-----------|--------------|
| **Initialization** | `lv_init()`, `lv_deinit()` |
| **Display** | `lv_display_create()`, `lv_display_set_flush_cb()`, `lv_display_set_buffers()` |
| **Input** | `lv_indev_create()`, `lv_indev_set_type()`, `lv_indev_set_read_cb()` |
| **Objects** | `lv_obj_create()`, `lv_obj_set_pos()`, `lv_obj_set_size()`, `lv_obj_align()` |
| **Button** | `lv_button_create()`, event with `LV_EVENT_CLICKED` |
| **Label** | `lv_label_create()`, `lv_label_set_text()`, `lv_label_set_long_mode()` |
| **Image** | `lv_image_create()`, `lv_image_set_src()`, `lv_image_set_scale()`, `lv_image_set_rotation()` |
| **Timer** | `lv_timer_create()`, `lv_timer_handler_run_in_period()` |
