# USB Device/Host API Reference (BL616/BL618)

## Overview

The BL616/BL618 contains a USB 2.0 OTG controller that supports both Device and Host modes. The USB stack is based on **CherryUSB**, a lightweight USB stack providing class drivers for common USB device classes.

## Source Files

- **CherryUSB Core**: `bouffalo_sdk/components/usb/cherryusb/`
- **Device Class Drivers**: `bouffalo_sdk/components/usb/cherryusb/class/` (CDC ACM, MSC, etc.)
- **BFLB USB HAL**: `bouffalo_sdk/drivers/lhal/include/bflb_usb.h`

---

## USB Initialization (Device Mode)

### 1. Get USB Device Handle

```c
#include "bflb_usb.h"

struct bflb_device_s *usb = bflb_device_get_by_name("usb");
```

### 2. Initialize USB Device

```c
#include "usbd_core.h"
#include "usb_platform.h"

// USB device configuration (defined in your descriptor file)
extern struct usbd_config_descriptor usb_desc;

void usb_device_init(void)
{
    struct bflb_device_s *usb;
    
    /* Get USB device */
    usb = bflb_device_get_by_name("usb");
    
    /* Initialize USB device stack */
    usbd_init(usb, &usb_desc);
    
    /* Enable USB */
    bflb_usb_enable(usb);
}
```

---

## USB Descriptors Structure

### Standard Descriptors

```c
#include "usbd_core.h"

/* Device Descriptor */
struct usbd_device_descriptor {
    uint8_t  bLength;            // Descriptor length (18)
    uint8_t  bDescriptorType;    // USB_DESC_TYPE_DEVICE
    uint16_t bcdUSB;             // USB spec version (0x0200 for USB 2.0)
    uint8_t  bDeviceClass;       // Device class
    uint8_t  bDeviceSubClass;    // Device subclass
    uint8_t  bDeviceProtocol;    // Device protocol
    uint8_t  bMaxPacketSize0;    // EP0 max packet size (64 for HS)
    uint16_t idVendor;           // Vendor ID
    uint16_t idProduct;          // Product ID
    uint16_t bcdDevice;          // Device release version
    uint8_t  iManufacturer;      // Manufacturer string index
    uint8_t  iProduct;           // Product string index
    uint8_t  iSerialNumber;      // Serial number string index
    uint8_t  bNumConfigurations; // Number of configurations
};

/* Configuration Descriptor */
struct usbd_config_descriptor {
    uint8_t  bLength;             // Descriptor length
    uint8_t  bDescriptorType;     // USB_DESC_TYPE_CONFIG
    uint16_t wTotalLength;        // Total length of descriptors
    uint8_t  bNumInterfaces;      // Number of interfaces
    uint8_t  bConfigurationValue; // Configuration value
    uint8_t  iConfiguration;      // Configuration string index
    uint8_t  bmAttributes;        // Attributes (bus powered, etc.)
    uint8_t  bMaxPower;           // Max power (mA/2)
};

/* Interface Descriptor */
struct usbd_interface_descriptor {
    uint8_t  bLength;            // Descriptor length
    uint8_t  bDescriptorType;    // USB_DESC_TYPE_INTERFACE
    uint8_t  bInterfaceNumber;   // Interface number
    uint8_t  bAlternateSetting;  // Alternate setting
    uint8_t  bNumEndpoints;       // Number of endpoints
    uint8_t  bInterfaceClass;     // Interface class (CDC, MSC, etc.)
    uint8_t  bInterfaceSubClass;  // Interface subclass
    uint8_t  bInterfaceProtocol;  // Interface protocol
    uint8_t  iInterface;         // Interface string index
};

/* Endpoint Descriptor */
struct usbd_endpoint_descriptor {
    uint8_t  bLength;          // Descriptor length
    uint8_t  bDescriptorType;   // USB_DESC_TYPE_ENDPOINT
    uint8_t  bEndpointAddress;  // Endpoint address (IN/OUT, ep number)
    uint8_t  bmAttributes;      // Transfer type (bulk, interrupt, etc.)
    uint16_t wMaxPacketSize;    // Max packet size
    uint8_t  bInterval;         // Polling interval (ms)
};
```

---

## CDC ACM (Communication Device Class - Abstract Control Model)

CDC ACM provides virtual COM port functionality (like a UART over USB).

### CDC ACM Header Files

```c
#include "usbd_cdc_acm.h"
```

### CDC ACM Configuration Example

```c
/* CDC ACM Endpoints */
#define CDC_INT_EP          0x81    // Interrupt IN endpoint
#define CDC_INT_EP_SIZE     16
#define CDC_BULK_IN_EP      0x82   // Bulk IN endpoint
#define CDC_BULK_IN_EP_SIZE 64
#define CDC_BULK_OUT_EP     0x02   // Bulk OUT endpoint
#define CDC_BULK_OUT_EP_SIZE 64

/* CDC ACM Interface Numbers */
#define CDC_CCI_INTERFACE   0     // Communication Control Interface
#define CDC_DCI_INTERFACE    1     // Data Interface

/* CDC ACM Descriptors (add to your descriptor array) */
const uint8_t cdc_acm_descriptor[] = {
    /* CCI Interface */
    0x09, 0x04, CDC_CCI_INTERFACE, 0x00, 0x01, 0x02, 0x02, 0x01, 0x00,
    /* Header Functional Descriptor */
    0x05, 0x24, 0x00, 0x10, 0x01,
    /* Call Management Functional Descriptor */
    0x05, 0x24, 0x01, 0x03, CDC_DCI_INTERFACE,
    /* ACM Functional Descriptor */
    0x04, 0x24, 0x02, 0x02,
    /* Union Functional Descriptor */
    0x05, 0x24, 0x06, CDC_CCI_INTERFACE, CDC_DCI_INTERFACE,
    /* Interrupt Endpoint */
    0x07, 0x05, CDC_INT_EP, 0x03, CDC_INT_EP_SIZE & 0xFF, CDC_INT_EP_SIZE >> 8, 0x09,
    
    /* DCI Interface */
    0x09, 0x04, CDC_DCI_INTERFACE, 0x00, 0x02, 0x0A, 0x00, 0x00, 0x00,
    /* Bulk OUT Endpoint */
    0x07, 0x05, CDC_BULK_OUT_EP, 0x02, CDC_BULK_OUT_EP_SIZE & 0xFF, CDC_BULK_OUT_EP_SIZE >> 8, 0x00,
    /* Bulk IN Endpoint */
    0x07, 0x05, CDC_BULK_IN_EP, 0x02, CDC_BULK_IN_EP_SIZE & 0xFF, CDC_BULK_IN_EP_SIZE >> 8, 0x00,
};
```

### CDC ACM API Functions

#### usbd_cdc_acm_init

Initialize CDC ACM device.

```c
int usbd_cdc_acm_init(struct bflb_device_s *usb,
                      uint8_t int_ep,
                      uint8_t bulk_in_ep,
                      uint8_t bulk_out_ep,
                      cdc_acm_linecoding_callback callback);
```

**Parameters:**
- `usb` - USB device handle
- `int_ep` - Interrupt endpoint address (IN)
- `bulk_in_ep` - Bulk IN endpoint address
- `bulk_out_ep` - Bulk OUT endpoint address
- `callback` - Line coding callback (for baud rate, parity, etc. changes)

**Returns:** 0 on success, negative error code on failure

---

#### usbd_cdc_acm_set_line_coding

Set line coding parameters (baud rate, data bits, stop bits, parity).

```c
int usbd_cdc_acm_set_line_coding(cdc_linecoding_t *linecoding);
```

**Parameters:**
- `linecoding` - Pointer to line coding structure

**Returns:** 0 on success

---

#### usbd_cdc_acm_get_line_coding

Get current line coding parameters.

```c
int usbd_cdc_acm_get_line_coding(cdc_linecoding_t *linecoding);
```

**Returns:** 0 on success

---

#### usbd_cdc_acm_set_break

Send break signal.

```c
int usbd_cdc_acm_set_break(uint16_t duration);
```

**Parameters:**
- `duration` - Break duration in milliseconds

**Returns:** 0 on success

---

#### usbd_cdc_acm_write

Write data to CDC ACM (transmit to host).

```c
int usbd_cdc_acm_write(const uint8_t *data, uint32_t len);
```

**Parameters:**
- `data` - Data to write
- `len` - Data length

**Returns:** Number of bytes written, negative on error

---

#### usbd_cdc_acm_read

Read data from CDC ACM (receive from host).

```c
int usbd_cdc_acm_read(uint8_t *data, uint32_t max_len);
```

**Parameters:**
- `data` - Buffer to store read data
- `max_len` - Maximum bytes to read

**Returns:** Number of bytes read, negative on error

---

#### usbd_cdc_acm_get_char

Read a single character from CDC ACM.

```c
int usbd_cdc_acm_get_char(uint8_t *c);
```

**Returns:** 0 on success, -1 if no data available

---

#### usbd_cdc_acm_poll

Poll for received data and return number of bytes available.

```c
int usbd_cdc_acm_poll(void);
```

**Returns:** Number of bytes available to read

---

## MSC (Mass Storage Class)

MSC allows the device to appear as a USB flash drive.

### MSC Header Files

```c
#include "usbd_msc.h"
```

### MSC Configuration Example

```c
/* MSC Endpoints */
#define MSC_BULK_IN_EP      0x81   // Bulk IN endpoint
#define MSC_BULK_IN_EP_SIZE 64
#define MSC_BULK_OUT_EP     0x02  // Bulk OUT endpoint
#define MSC_BULK_OUT_EP_SIZE 64

/* MSC Interface Number */
#define MSC_INTERFACE       0

/* MSC Descriptors */
const uint8_t msc_descriptor[] = {
    /* Interface Descriptor */
    0x09, 0x04, MSC_INTERFACE, 0x00, 0x02, 0x08, 0x06, 0x50, 0x00,
    /* Full Speed Endpoint Descriptor - Bulk IN */
    0x07, 0x05, MSC_BULK_IN_EP, 0x02, MSC_BULK_IN_EP_SIZE & 0xFF, MSC_BULK_IN_EP_SIZE >> 8, 0x00,
    /* Full Speed Endpoint Descriptor - Bulk OUT */
    0x07, 0x05, MSC_BULK_OUT_EP, 0x02, MSC_BULK_OUT_EP_SIZE & 0xFF, MSC_BULK_OUT_EP_SIZE >> 8, 0x00,
};
```

### MSC API Functions

#### usbd_msc_init

Initialize MSC device.

```c
int usbd_msc_init(struct bflb_device_s *usb,
                  uint8_t bulk_in_ep,
                  uint8_t bulk_out_ep,
                  uint32_t block_size,
                  uint32_t block_count,
                  msc_read_callback read_callback,
                  msc_write_callback write_callback);
```

**Parameters:**
- `usb` - USB device handle
- `bulk_in_ep` - Bulk IN endpoint address
- `bulk_out_ep` - Bulk OUT endpoint address
- `block_size` - Storage block size (typically 512)
- `block_count` - Number of blocks (capacity = block_size * block_count)
- `read_callback` - Callback for READ(10) SCSI commands
- `write_callback` - Callback for WRITE(10) SCSI commands

**Returns:** 0 on success, negative error code on failure

---

#### usbd_msc_sector_read

Read sectors from storage (callback implementation).

```c
int usbd_msc_sector_read(uint32_t sector, uint8_t *buffer, uint32_t num);
```

---

#### usbd_msc_sector_write

Write sectors to storage (callback implementation).

```c
int usbd_msc_sector_write(uint32_t sector, uint8_t *buffer, uint32_t num);
```

---

## USB Device Configuration Example

Complete descriptor setup for CDC ACM:

```c
#include "usbd_core.h"
#include "usbd_cdc_acm.h"

/* String Descriptors */
const uint8_t langid_str_desc[] = { 0x04, 0x03, 0x09, 0x04 };
const uint8_t mfg_str_desc[] = { 0x12, 0x03, 'B', 0, 'L', 0, 'I', 0, 'T', 0, 'K', 0, 'E', 0, 'R', 0 };
const uint8_t prod_str_desc[] = { 0x1C, 0x03, 'B', 0, 'L', 0, '6', 0, '1', 0, '6', 0, ' ', 0, 'U', 0, 'S', 0, 'B', 0, ' ', 0, 'D', 0, 'E', 0, 'V', 0 };
const uint8_t serial_str_desc[] = { 0x0A, 0x03, '0', 0, '0', 0, '0', 0, '1', 0 };

/* Full Device Descriptor */
const uint8_t full_dev_desc[] = {
    /* Device Descriptor */
    0x12, 0x01, 0x00, 0x02, 0x02, 0x00, 0x00, 0x40, 0x9A, 0x10, 0x25, 0x30, 0x00, 0x00, 0x01, 0x02, 0x03,
    /* Configuration Descriptor */
    0x09, 0x02, 0x00, 0x00, 0x02, 0x01, 0x00, 0x80, 0x32,
    /* CDC ACM Descriptors (from above) */
    // ... include cdc_acm_descriptor array here ...
    /* Interface Association Descriptor (for CDC) */
    0x08, 0x0B, CDC_CCI_INTERFACE, 0x02, 0x02, 0x02, 0x00, 0x00,
};

/* Device configuration structure */
struct usbd_config_descriptor usb_desc = {
    .device_descriptor = (struct usbd_device_descriptor *)full_dev_desc,
    .config_descriptor = /* pointer to config in full_dev_desc */,
    .string_descriptors = { langid_str_desc, mfg_str_desc, prod_str_desc, serial_str_desc },
    .num_string_descriptors = 4,
};
```

---

## Working Examples

### CDC ACM Virtual COM Port Example

```c
#include "bflb_usb.h"
#include "usbd_core.h"
#include "usbd_cdc_acm.h"

static struct bflb_device_s *usb;

static void cdc_acm_linecoding_callback(cdc_linecoding_t *linecoding)
{
    printf("Baud: %lu, Data: %d, Stop: %d, Parity: %d\r\n",
           linecoding->bitrate,
           linecoding->datatype,
           linecoding->format,
           linecoding->paritytype);
}

void cdc_acm_echo_example(void)
{
    uint8_t buf[64];
    int len;
    
    /* Initialize USB device */
    usb = bflb_device_get_by_name("usb");
    usbd_init(usb, &usb_desc);
    bflb_usb_enable(usb);
    
    /* Initialize CDC ACM with callbacks */
    usbd_cdc_acm_init(usb,
                      CDC_INT_EP,
                      CDC_BULK_IN_EP,
                      CDC_BULK_OUT_EP,
                      cdc_acm_linecoding_callback);
    
    printf("CDC ACM initialized, waiting for host connection...\r\n");
    
    while (1) {
        /* Poll for received data */
        len = usbd_cdc_acm_poll();
        if (len > 0) {
            /* Read and echo back */
            len = usbd_cdc_acm_read(buf, sizeof(buf));
            if (len > 0) {
                /* Echo received data back to host */
                usbd_cdc_acm_write(buf, len);
            }
        }
    }
}
```

### MSC USB Flash Drive Example

```c
#include "bflb_usb.h"
#include "usbd_core.h"
#include "usbd_msc.h"

#define BLOCK_SIZE   512
#define BLOCK_COUNT  1024  // 512KB storage

static struct bflb_device_s *usb;
static uint8_t msc_storage[BLOCK_SIZE * BLOCK_COUNT];

static int msc_read_callback(uint32_t sector, uint8_t *buffer, uint32_t num)
{
    memcpy(buffer, msc_storage + (sector * BLOCK_SIZE), num * BLOCK_SIZE);
    return 0;
}

static int msc_write_callback(uint32_t sector, uint8_t *buffer, uint32_t num)
{
    memcpy(msc_storage + (sector * BLOCK_SIZE), buffer, num * BLOCK_SIZE);
    return 0;
}

void msc_storage_example(void)
{
    /* Initialize USB device */
    usb = bflb_device_get_by_name("usb");
    usbd_init(usb, &usb_desc);
    bflb_usb_enable(usb);
    
    /* Initialize MSC */
    usbd_msc_init(usb,
                  MSC_BULK_IN_EP,
                  MSC_BULK_OUT_EP,
                  BLOCK_SIZE,
                  BLOCK_COUNT,
                  msc_read_callback,
                  msc_write_callback);
    
    printf("MSC initialized, appearing as %lu KB USB drive\r\n",
           (BLOCK_SIZE * BLOCK_COUNT) / 1024);
    
    while (1) {
        /* MSC operations handled automatically by callback */
        bflb_mdelay(1000);
    }
}
```

### Combined CDC ACM + MSC (Multi-Interface Device)

```c
#include "bflb_usb.h"
#include "usbd_core.h"
#include "usbd_cdc_acm.h"
#include "usbd_msc.h"

/* Interface Numbers */
#define CDC_CCI_INTERFACE   0
#define CDC_DCI_INTERFACE   1
#define MSC_INTERFACE       2

void usb_combined_example(void)
{
    usb = bflb_device_get_by_name("usb");
    usbd_init(usb, &usb_desc);
    bflb_usb_enable(usb);
    
    /* Initialize CDC ACM */
    usbd_cdc_acm_init(usb, 0x81, 0x82, 0x02, NULL);
    
    /* Initialize MSC (using different endpoints) */
    usbd_msc_init(usb, 0x83, 0x04, 512, 2048, msc_read_callback, msc_write_callback);
    
    printf("Combined CDC ACM + MSC device initialized\r\n");
}
```

---

## Endpoint Addresses

| Endpoint | Address | Direction | Type | Max Packet Size |
|----------|---------|-----------|------|-----------------|
| EP0 | 0x00/0x80 | Control | Control | 64 |
| CDC INT | 0x81 | IN | Interrupt | 16 |
| CDC Bulk IN | 0x82 | IN | Bulk | 64 |
| CDC Bulk OUT | 0x02 | OUT | Bulk | 64 |
| MSC Bulk IN | 0x83 | IN | Bulk | 64 |
| MSC Bulk OUT | 0x04 | OUT | Bulk | 64 |

---

## Notes

1. **USB OTG**: The BL616/BL618 USB controller supports OTG. Use `bflb_usb_set_mode()` to switch between device and host modes.

2. **DMA**: USB supports DMA transfers for better performance. Enable with `usbd_dma_enable()`.

3. **String Descriptors**: Must use UTF-16LE encoding (2 bytes per character with trailing 0).

4. ** VID/PID**: Use Bouffalo's vendor ID (0x25D7) or obtain your own from USB-IF.

5. **Driver Installation**: On Windows, a `.inf` file or WinUSB driver may be required for CDC ACM devices.
