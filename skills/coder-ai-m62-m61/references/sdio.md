# SDIO/SDH Driver Documentation

**Hardware Base:** `SDH_BASE = 0x2000C800`

**Chip Support:** BL616, BL616CL, BL618DG

---

## 1. Architecture Overview

| Module | Description |
|------|------|
| **SDH** | Secure Digital Host - Low-level SD/MMC controller, supports DMA/ADMA |
| **SDIO2** | SDIO 2.0 protocol layer (backward compatible) |
| **SDIO3** | SDIO 3.0 protocol layer (high performance, supports SDR104/SDR50/DDR50) |

---

## 2. SDH (Secure Digital Host)

### 2.1 Key Features

- **Data transfer direction:** `SDH_TRANSFER_DIR_WR` (send) / `SDH_TRANSFER_DIR_RD` (receive)
- **Data bus width:** 1-bit / 4-bit / 8-bit
- **Endian mode:** Little / Half-Word Big / Big
- **DMA type:** SDMA / ADMA1 / ADMA2
- **Supports SDIO interrupts**

### 2.2 Status Flags

```c
#define SDH_NORMAL_STA_CARD_INSERT    (1 << 6)  // Card inserted
#define SDH_NORMAL_STA_CARD_REMOVE    (1 << 7)  // Card removed
#define SDH_NORMAL_STA_CMD_COMP       (1 << 0)  // Command complete
#define SDH_NORMAL_STA_TRAN_COMP      (1 << 1)  // Transfer complete
#define SDH_NORMAL_STA_DMA_INT        (1 << 3)  // DMA interrupt
#define SDH_NORMAL_STA_BUFF_WR_RDY    (1 << 4)  // Buffer write ready
#define SDH_NORMAL_STA_BUFF_RD_RDY    (1 << 5)  // Buffer read ready
```

### 2.3 Error Status

```c
#define SDH_ERROR_STA_CMD_TIMEOUT     (1 << 16)  // Command timeout
#define SDH_ERROR_STA_CMD_CRC_ERR     (1 << 17)  // Command CRC error
#define SDH_ERROR_STA_DATA_TIMEOUT    (1 << 20)  // Data timeout
#define SDH_ERROR_STA_DATA_CRC_ERR    (1 << 21)  // Data CRC error
#define SDH_ERROR_STA_ADMA_ERR        (1 << 25)  // ADMA error
```

---

## 3. Data Structures

### 3.1 SDH Configuration

```c
struct bflb_sdh_config_s {
    uint8_t dma_fifo_th;  // FIFO threshold: 64/128/192/256
    uint8_t dma_burst;   // Burst length: 32/64/128/256
    uint8_t power_vol;   // Power voltage
};
```

### 3.2 Command Configuration

```c
struct bflb_sdh_cmd_cfg_s {
    uint8_t index;      // Command index (0-63)
    uint8_t cmd_type;   // Command type: NORMAL/SUSPEND/RESUME/ABORT
    uint8_t resp_type;  // Response type: NONE/R1/R1b/R2/R3/R4/R5/R5b/R6/R7
    uint32_t argument;  // Command argument
    uint32_t resp[4];   // Response data
};
```

### 3.3 Data Configuration

```c
struct bflb_sdh_data_cfg_s {
    uint8_t data_dir;      // SDH_TRANSFER_DIR_RD or SDH_TRANSFER_DIR_WR
    uint8_t data_type;     // NORMAL/TUNING/BOOT/BOOT_CONTINU
    uint8_t auto_cmd_mode; // AUTO_CMD_DISABLE/CMD12/CMD23
    uint16_t block_size;   // Block size
    uint16_t block_count;  // Block count
    
    // ADMA2 configuration
    bool adma2_hw_desc_raw_mode;
    struct bflb_sdh_data_tranfer_s *adma_tranfer;
    uint32_t adma_tranfer_cnt;
    struct bflb_sdh_adma2_hw_desc_s *adma2_hw_desc;
    uint32_t adma2_hw_desc_cnt;
};
```

---

## 4. API Reference

### 4.1 Initialization

```c
int bflb_sdh_init(struct bflb_device_s *dev, struct bflb_sdh_config_s *cfg);
```

**Example:**
```c
struct bflb_device_s *sdh;
struct bflb_sdh_config_s sdh_cfg = {
    .dma_fifo_th = SDH_DMA_FIFO_THRESHOLD_256,
    .dma_burst = SDH_DMA_BURST_256,
    .power_vol = 0,
};

sdh = bflb_device_get_by_name("sdh");
if (sdh) {
    bflb_sdh_init(sdh, &sdh_cfg);
}
```

### 4.2 Card Insertion Detection

```c
// Enable card insertion status interrupt
bflb_sdh_sta_int_en(sdh, SDH_NORMAL_STA_CARD_INSERT | SDH_NORMAL_STA_CARD_REMOVE, true);

// Polling-based card insertion detection
uint32_t sta = bflb_sdh_sta_get(sdh);
if (sta & SDH_NORMAL_STA_CARD_INSERT) {
    printf("Card inserted\r\n");
}

// Get card detect pin status (feature control)
int inserted = bflb_sdh_feature_control(sdh, SDH_CMD_GET_PRESENT_STA_CARD_INSERTED, 0);
```

### 4.3 Data Transfer

```c
int bflb_sdh_tranfer_start(struct bflb_device_s *dev, 
                           struct bflb_sdh_cmd_cfg_s *cmd_cfg, 
                           struct bflb_sdh_data_cfg_s *data_cfg);

int bflb_sdh_get_resp(struct bflb_device_s *dev, struct bflb_sdh_cmd_cfg_s *cmd_cfg);
```

### 4.4 Status Management

```c
uint32_t bflb_sdh_sta_get(struct bflb_device_s *dev);          // Get status
void bflb_sdh_sta_clr(struct bflb_device_s *dev, uint32_t sta_bit);  // Clear status
void bflb_sdh_sta_int_en(struct bflb_device_s *dev, uint32_t sta_bit, bool en);  // Interrupt enable
```

### 4.5 Feature Control

```c
int bflb_sdh_feature_control(struct bflb_device_s *dev, int cmd, uintptr_t arg);

// Common commands:
SDH_CMD_SET_BUS_WIDTH          // Set bus width
SDH_CMD_SET_HS_MODE_EN        // High-speed mode enable
SDH_CMD_SET_BUS_CLK_DIV        // Set clock divider
SDH_CMD_SET_INTERNAL_CLK_EN    // Internal clock enable
SDH_CMD_GET_INTERNAL_CLK_STABLE  // Get clock stable status
SDH_CMD_SOFT_RESET_ALL        // Software reset
```

---

## 5. SDIO2 API

SDIO2 is the SDIO 2.0 backward-compatible mode.

```c
int bflb_sdio2_init(struct bflb_device_s *dev, uint32_t dnld_size_max);
int bflb_sdio2_deinit(struct bflb_device_s *dev);

// Transfer queue
int bflb_sdio2_dnld_port_push(struct bflb_device_s *dev, bflb_sdio2_trans_desc_t *trans_desc);
int bflb_sdio2_upld_port_push(struct bflb_device_s *dev, bflb_sdio2_trans_desc_t *trans_desc);
int bflb_sdio2_dnld_port_pop(struct bflb_device_s *dev, bflb_sdio2_trans_desc_t *trans_desc);
int bflb_sdio2_upld_port_pop(struct bflb_device_s *dev, bflb_sdio2_trans_desc_t *trans_desc);

// Interrupt callback
int bflb_sdio2_irq_attach(struct bflb_device_s *dev, bflb_sdio2_irq_cb_t irq_event_cb, void *arg);

// Feature control
int bflb_sdio2_feature_control(struct bflb_device_s *dev, int cmd, uintptr_t arg);
```

---

## 6. SDIO3 API

SDIO3 is the high-performance SDIO 3.0 mode, supporting SDR104/SDR50/DDR50.

```c
int bflb_sdio3_init(struct bflb_device_s *dev, struct bflb_sdio3_config_s *cfg);
int bflb_sdio3_deinit(struct bflb_device_s *dev);

// Configuration structure
struct bflb_sdio3_config_s {
    uint8_t func_num;              // Function number: 1~2
    uint32_t ocr;                  // Operating voltage range
    uint32_t cap_flag;             // Capability flags
    uint32_t func1_dnld_size_max;  // Function 1 download max size
    uint32_t func2_dnld_size_max;  // Function 2 download max size
};

// Transfer interface
int bflb_sdio3_dnld_push(struct bflb_device_s *dev, bflb_sdio3_trans_desc_t *trans_desc);
int bflb_sdio3_upld_push(struct bflb_device_s *dev, bflb_sdio3_trans_desc_t *trans_desc);
int bflb_sdio3_dnld_pop(struct bflb_device_s *dev, bflb_sdio3_trans_desc_t *trans_desc, uint8_t func);
int bflb_sdio3_upld_pop(struct bflb_device_s *dev, bflb_sdio3_trans_desc_t *trans_desc, uint8_t func);

// Custom registers
int bflb_sdio3_custom_reg_read(struct bflb_device_s *dev, uint16_t reg_offset, void *buff, uint16_t len);
int bflb_sdio3_custom_reg_write(struct bflb_device_s *dev, uint16_t reg_offset, void *buff, uint16_t len);

// Interrupt callback
int bflb_sdio3_irq_attach(struct bflb_device_s *dev, bflb_sdio3_irq_cb_t irq_event_cb, void *arg);

// Feature control
int bflb_sdio3_feature_control(struct bflb_device_s *dev, int cmd, uintptr_t arg);
```

---

## 7. Working Code Examples

### 7.1 SDH Initialization and Card Detection

```c
#include "bflb_sdh.h"
#include "bflb_irq.h"

static struct bflb_device_s *sdh_dev;

void sdh_isr(int irq, void *arg)
{
    uint32_t sta = bflb_sdh_sta_get(sdh_dev);
    
    if (sta & SDH_NORMAL_STA_CARD_INSERT) {
        printf("Card inserted\r\n");
        bflb_sdh_sta_clr(sdh_dev, SDH_NORMAL_STA_CARD_INSERT);
    }
    if (sta & SDH_NORMAL_STA_CARD_REMOVE) {
        printf("Card removed\r\n");
        bflb_sdh_sta_clr(sdh_dev, SDH_NORMAL_STA_CARD_REMOVE);
    }
    
    /* Handle other interrupts... */
}

int sdh_card_init(void)
{
    struct bflb_sdh_config_s cfg = {
        .dma_fifo_th = SDH_DMA_FIFO_THRESHOLD_256,
        .dma_burst = SDH_DMA_BURST_256,
        .power_vol = 0,
    };
    
    sdh_dev = bflb_device_get_by_name("sdh");
    if (!sdh_dev) {
        printf("Get SDH device failed\r\n");
        return -1;
    }
    
    bflb_sdh_init(sdh_dev, &cfg);
    
    /* Register interrupt */
    bflb_irq_register(sdh_dev->irq_num, sdh_isr, NULL);
    bflb_irq_enable(sdh_dev->irq_num);
    
    /* Enable card insert/remove interrupts */
    bflb_sdh_sta_int_en(sdh_dev, 
                        SDH_NORMAL_STA_CARD_INSERT | SDH_NORMAL_STA_CARD_REMOVE, 
                        true);
    
    return 0;
}
```

### 7.2 SDIO3 Full Initialization

```c
#include "bflb_sdio3.h"

static struct bflb_device_s *sdio3_dev;

void sdio3_irq_callback(void *arg, uint32_t irq_event, bflb_sdio3_trans_desc_t *trans_desc)
{
    switch (irq_event) {
        case SDIO3_IRQ_EVENT_DNLD_CPL:
            printf("Download complete\r\n");
            break;
        case SDIO3_IRQ_EVENT_UPLD_CPL:
            printf("Upload complete\r\n");
            break;
        case SDIO3_IRQ_EVENT_ERR_CRC:
            printf("CRC error\r\n");
            break;
        case SDIO3_IRQ_EVENT_ERR_ADMA:
            printf("ADMA error\r\n");
            break;
        default:
            printf("IRQ event: %u\r\n", irq_event);
            break;
    }
}

int sdio3_init(void)
{
    struct bflb_sdio3_config_s cfg = {
        .func_num = 1,
        .ocr = 0x00300000,  // 3.0V-3.4V
        .cap_flag = SDIO3_CAP_FLAG_SDR104 | SDIO3_CAP_FLAG_SDR50,
        .func1_dnld_size_max = 4096,
        .func2_dnld_size_max = 0,
    };
    
    sdio3_dev = bflb_device_get_by_name("sdio3");
    if (!sdio3_dev) {
        printf("Get SDIO3 device failed\r\n");
        return -1;
    }
    
    int ret = bflb_sdio3_init(sdio3_dev, &cfg);
    if (ret != 0) {
        printf("SDIO3 init failed: %d\r\n", ret);
        return ret;
    }
    
    /* Register interrupt callback */
    bflb_sdio3_irq_attach(sdio3_dev, sdio3_irq_callback, NULL);
    
    return 0;
}
```

### 7.3 Data Read

```c
int sdh_read_blocks(uint32_t start_block, uint16_t block_count, uint8_t *buffer)
{
    struct bflb_sdh_cmd_cfg_s cmd_cfg = {
        .index = 17,  // READ_SINGLE_BLOCK
        .cmd_type = SDH_CMD_TPYE_NORMAL,
        .resp_type = SDH_RESP_TPYE_R1,
        .argument = start_block,
    };
    
    struct bflb_sdh_data_cfg_s data_cfg = {
        .data_dir = SDH_TRANSFER_DIR_RD,
        .data_type = SDH_DATA_TPYE_NORMAL,
        .auto_cmd_mode = SDH_AUTO_CMD_DISABLE,
        .block_size = 512,
        .block_count = block_count,
        .adma2_hw_desc_raw_mode = false,
    };
    
    struct bflb_sdh_data_tranfer_s adma_tranfer = {
        .address = buffer,
        .length = block_count * 512,
        .int_en = true,
    };
    
    data_cfg.adma_tranfer = &adma_tranfer;
    data_cfg.adma_tranfer_cnt = 1;
    
    int ret = bflb_sdh_tranfer_start(sdh_dev, &cmd_cfg, &data_cfg);
    if (ret != 0) {
        printf("Read transfer failed: %d\r\n", ret);
        return ret;
    }
    
    /* Get response */
    bflb_sdh_get_resp(sdh_dev, &cmd_cfg);
    
    return 0;
}
```

### 7.4 Data Write

```c
int sdh_write_blocks(uint32_t start_block, uint16_t block_count, uint8_t *buffer)
{
    struct bflb_sdh_cmd_cfg_s cmd_cfg = {
        .index = 24,  // WRITE_BLOCK
        .cmd_type = SDH_CMD_TPYE_NORMAL,
        .resp_type = SDH_RESP_TPYE_R1,
        .argument = start_block,
    };
    
    struct bflb_sdh_data_cfg_s data_cfg = {
        .data_dir = SDH_TRANSFER_DIR_WR,
        .data_type = SDH_DATA_TPYE_NORMAL,
        .auto_cmd_mode = SDH_AUTO_CMD_DISABLE,
        .block_size = 512,
        .block_count = block_count,
        .adma2_hw_desc_raw_mode = false,
    };
    
    struct bflb_sdh_data_tranfer_s adma_tranfer = {
        .address = buffer,
        .length = block_count * 512,
        .int_en = true,
    };
    
    data_cfg.adma_tranfer = &adma_tranfer;
    data_cfg.adma_tranfer_cnt = 1;
    
    int ret = bflb_sdh_tranfer_start(sdh_dev, &cmd_cfg, &data_cfg);
    if (ret != 0) {
        printf("Write transfer failed: %d\r\n", ret);
        return ret;
    }
    
    bflb_sdh_get_resp(sdh_dev, &cmd_cfg);
    
    return 0;
}
```

### 7.5 SDIO3 Upload/Download

```c
int sdio3_upload_data(uint8_t func, uint16_t data_len, uint8_t *buffer)
{
    bflb_sdio3_trans_desc_t trans_desc = {
        .func = func,
        .buff_len = data_len,
        .data_len = data_len,
        .buff = buffer,
        .user_arg = NULL,
    };
    
    return bflb_sdio3_upld_push(sdio3_dev, &trans_desc);
}

int sdio3_download_data(uint8_t func, uint16_t data_len, uint8_t *buffer)
{
    bflb_sdio3_trans_desc_t trans_desc = {
        .func = func,
        .buff_len = data_len,
        .data_len = data_len,
        .buff = buffer,
        .user_arg = NULL,
    };
    
    return bflb_sdio3_dnld_push(sdio3_dev, &trans_desc);
}
```

---

## 8. ADMA2 Descriptor Table

```
|----------------|---------------|-------------|--------------------------|
| Address field  |     Length    | Reserved    |         Attribute        |
|----------------|---------------|-------------|--------------------------|
|63            32|31           16|15         06|05  |04  |03|02 |01 |00   |
|----------------|---------------|-------------|----|----|--|---|---|-----|
| 32-bit address | 16-bit length | 0000000000  |Act2|Act1| 0|Int|End|Valid|
|----------------|---------------|-------------|----|----|--|---|---|-----|

Attributes:
- Valid (bit 0): Descriptor valid
- End (bit 1): Descriptor end
- Int (bit 2): DMA interrupt
- Act (bit 4-5): 00=NOP, 01=Reserved, 10=Transfer data, 11=Link descriptor

Maximum descriptor length: 64KB (0xFFFF + 1)
```

---

## 9. Register Quick Reference

**SDH_BASE = 0x2000C800**

| Offset | Name | Description |
|------|------|------|
| 0x00 | SDH_SYS_ADDR | System address register |
| 0x04 | SDH_BLOCK_SIZE | Block size register |
| 0x06 | SDH_BLOCK_COUNT | Block count register |
| 0x08 | SDH_ARGUMENT | Command argument register |
| 0x0C | SDH_TRANS_MOD | Transfer mode register |
| 0x0E | SDH_CMD | Command register |
| 0x10-0x14 | SDH_RESP | Response register 0-3 |
| 0x18 | SDH_DATA_PORT | Data port |
| 0x1C | SDH_PRESENT_STA | Present state |
| 0x20 | SDH_HOST_CTL | Host control |
| 0x24 | SDH_PWR_CTL | Power control |
| 0x28 | SDH_CLK_CTL | Clock control |
| 0x2C | SDH_TOUT_CTL | Timeout control |
| 0x30 | SDH_SWRST | Software reset |
| 0x34 | SDH_NOR_INTS_STA | Normal interrupt status |
| 0x36 | SDH_ERR_INTS_STA | Error interrupt status |
| 0x38 | SDH_NOR_INTS_EN | Normal interrupt enable |
| 0x3A | SDH_ERR_INTS_EN | Error interrupt enable |
| 0x3C | SDH_NOR_INTS_SIGNAL_EN | Normal interrupt signal enable |
| 0x3E | SDH_ERR_INTS_SIGNAL_EN | Error interrupt signal enable |
| 0x40 | SDH_ADMA_ES | ADMA status |
| 0x48 | SDH_ADMA_ADDR | ADMA address |
