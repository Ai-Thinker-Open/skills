# BL616/618 Matter Factory Data (MFD) Technical Documentation

## Overview

Matter is a smart home interoperability standard formulated by the CSA (Connectivity Standards Alliance), aimed at unifying device communication protocols across different ecosystems. BL616/618, as wireless MCUs supporting the Matter protocol, use the **mfd** (Matter Factory Data) module to store and manage the core data required for device authentication.

The MFD module is responsible for reading factory-preset authentication data from a specific storage area of the chip's Flash, including sensitive information such as device certificates, private keys, PAI certificates, and CD (Certificate Declaration). This data is invoked by the Matter protocol stack during the device commissioning process for device identity verification and encrypted communication.

## MFD Version Information

The MFD module version is **1.6.1**, defined as follows:

```c
#define VERSION_MFD_MAJOR 1
#define VERSION_MFD_MINOR 6
#define VERSION_MFD_PATCH 1
```

## MFD Initialization

Before using any MFD data reading interface, `mfd_init()` must be called to initialize the factory data area:

```c
bool mfd_init(void);
```

`mfd_init()` performs the following operations:

1. Initialize Flash access control
2. Locate the storage address of the factory data area in Flash
3. Verify the integrity of the data area
4. Decrypt sensitive data that needs encryption (e.g., private keys)
5. Prepare the data reading environment

The return value indicates whether initialization succeeded. Only after successful initialization can other MFD data reading interfaces be used normally.

## Device Certificate Interfaces

### DAC Certificate Operations

The Device Attestation Certificate (DAC) is the core identity credential of a Matter device.

```c
int mfd_getDacCert(uint8_t *p, uint32_t size);
uint8_t *mfd_getDacCertPtr(uint32_t *psize);
```

- `mfd_getDacCert()`: Copies the DAC certificate to a specified buffer and returns the read status
- `mfd_getDacCertPtr()`: Returns a pointer to the DAC certificate in memory directly; `psize` stores the certificate length

### DAC Private Key Operations

The device private key is used for certificate signature verification and must be securely stored:

```c
int mfd_getDacPrivateKey(uint8_t *p, uint32_t size);
uint8_t *mfd_getDacPrivateKeyPtr(uint32_t *psize);
```

The private key data is stored in encrypted form in Flash; `mfd_init()` handles the decryption.

### PAI Certificate

The PAI (Product Attestation Intermediate) certificate is the intermediate layer in the certificate chain:

```c
int mfd_getPaiCert(uint8_t *p, uint32_t size);
```

### CD Certificate Declaration

The CD (Certificate Declaration) is used to declare the device's certification status:

```c
int mfd_getCd(uint8_t *p, uint32_t size);
```

## Device Commissioning Parameters

### Passcode and Discriminator

```c
int mfd_getPasscode(uint8_t *p, uint32_t size);
int mfd_getDiscriminator(uint8_t *p, uint32_t size);
```

- `mfd_getPasscode()`: Retrieves the device passcode (8 digits), used for SPAKE2+ authentication
- `mfd_getDiscriminator()`: Retrieves the device discriminator, used for BLE advertising and service discovery

### Rotating Device Unique ID

```c
int mfd_getRotatingDeviceIdUniqueId(uint8_t *p, uint32_t size);
```

The rotating device unique ID is used to generate the device rotate ID, enhancing device identification privacy.

## Vendor Information

### Vendor ID and Name

```c
int mfd_getVendorId(uint8_t *buf, uint32_t size);
int mfd_getVendorName(char *buf, uint32_t size);
```

Vendor ID is a unique identifier assigned by CSA, and Vendor Name is a human-readable vendor name string.

### Product Information

```c
int mfd_getProductId(uint8_t *buf, uint32_t size);
int mfd_getProductName(char *buf, uint32_t size);
```

Product ID and Product Name are used to identify specific product models.

### Hardware Version

```c
int mfd_getHardwareVersion(uint8_t *buf, uint32_t size);
int mfd_getHardwareVersionString(char *buf, uint32_t size);
```

Hardware version information is used for firmware compatibility and device identification.

## SPAKE2+ Authentication Parameters

SPAKE2+ is a password-based authentication protocol used to establish secure connections over untrusted networks. The Matter protocol uses SPAKE2+ to implement identity verification during device pairing.

### SPAKE2+ Iteration Factor

```c
int mfd_getSapke2It(uint8_t *p, uint32_t size);
```

IT (Iterations) is the iteration count of the PBKDF function, used to increase brute-force cracking difficulty.

### SPAKE2+ Salt

```c
int mfd_getSapke2Salt(uint8_t *p, uint32_t size);
```

Salt is a randomly generated salt value, used together with the iteration factor to derive authentication keys.

### SPAKE2+ Verifier

```c
int mfd_getSapke2Verifier(uint8_t *p, uint32_t size);
```

The Verifier is generated based on the user passcode; the Commissioner and Device each compute it and compare to complete mutual authentication.

## Common Data Access Interface

### Element ID Query

MFD provides a generic data access interface based on Element ID:

```c
int mfd_getElementById(int16_t id, uint8_t *buf, uint32_t size);
```

Any data item in the factory data area can be accessed via Element ID. This approach is suitable for accessing extended data fields not covered by standard MFD interfaces.

## DAC Certificate Chain Structure

Matter devices use a three-layer certificate chain structure to implement trust delegation:

```
┌─────────────────┐
│      CD         │  Certificate Declaration
│  (Self-signed)  │  Declares device meets Matter certification requirements
└────────┬────────┘
         │ Verify signature
         ▼
┌─────────────────┐
│      PAI        │  Product Attestation Intermediate
│  (Issued by CSA)│  Signed by CSA root certificate
└────────┬────────┘
         │ Verify signature
         ▼
┌─────────────────┐
│      DAC        │  Device Attestation Certificate
│  (Vendor-issued)│  Signed by PAI, contains unique device info
└─────────────────┘
```

### Certificate Chain Verification Process

1. **CD Verification**: Verify the self-signed nature of the CD certificate to confirm the device has declared its certification status
2. **PAI Verification**: Use the CSA root certificate to verify the PAI certificate's signature, confirming the intermediate certificate's legitimacy
3. **DAC Verification**: Use the PAI certificate to verify the DAC certificate's signature, confirming the device identity

This layered structure achieves:
- **Trust Delegation**: Flexible certificate management through intermediate certificates
- **Revocation Control**: Individual PAI or DAC can be revoked without affecting other devices
- **Audit Traceability**: The device's complete certification path can be traced

## Matter Commissioning Process

Device commissioning is the process of joining a Matter device into a Matter network, consisting of the following stages:

### 1. Discovery

After power-up, the device performs service discovery via BLE advertising or an established IP network:

- The device sends BLE advertisements containing Matter Service Data
- Or announces Matter device services via DNS-SD on the LAN
- The Commissioner retrieves the device's Discriminator and Vendor ID

### 2. BLE/PiV Connection Establishment

- The Commissioner establishes a BLE connection based on discovered device information
- Or establishes a secure channel over the IP network
- Exchange protocol version and capability information

### 3. SPAKE2+ Authentication

This is the core security step of device pairing:

```
Commissioner                    Device
     │                             │
     │<-- Device attestation (PAI, DAC) --│
     │                             │
     │  Verify device cert chain   │
     │                             │
     │--- Commissioner identity proof --->│
     │                             │
     │  SPAKE2+ verifier comparison│
     │                             │
     │<-- Auth success/failure ----│
```

- The device sends DAC and PAI certificates to the Commissioner
- The Commissioner verifies the certificate chain integrity
- Execute SPAKE2+ protocol using Passcode, Salt, and Iterations
- Establish shared key after successful verification

### 4. Network Commissioning

After authentication completes, the Commissioner guides the device through network configuration:

- The device scans for and joins a Wi-Fi or Thread network
- The device obtains necessary network configuration parameters
- The device completes registration in the Matter network
- Establish secure Matter data channels

## Code Examples

### MFD Initialization and Data Reading

```c
#include "bl_mfd.h"
#include <stdio.h>

void matter_device_init(void)
{
    uint32_t size;
    uint8_t *dac_cert;
    uint8_t *dac_key;
    uint8_t vendor_id[2];
    uint8_t product_id[2];
    uint8_t passcode[16];
    uint8_t discriminator[2];
    uint8_t spake2_it[4];
    uint8_t spake2_salt[32];
    uint8_t spake2_verifier[256];
    
    /* Initialize MFD module */
    if (!mfd_init()) {
        printf("MFD init failed\r\n");
        return;
    }
    printf("MFD init success\r\n");
    
    /* Get DAC certificate */
    dac_cert = mfd_getDacCertPtr(&size);
    if (dac_cert) {
        printf("DAC Cert size: %u\r\n", size);
    }
    
    /* Get DAC private key */
    dac_key = mfd_getDacPrivateKeyPtr(&size);
    if (dac_key) {
        printf("DAC Private Key size: %u\r\n", size);
    }
    
    /* Get vendor and product info */
    mfd_getVendorId(vendor_id, sizeof(vendor_id));
    mfd_getProductId(product_id, sizeof(product_id));
    printf("Vendor ID: 0x%04x, Product ID: 0x%04x\r\n",
           (vendor_id[0] << 8) | vendor_id[1],
           (product_id[0] << 8) | product_id[1]);
    
    /* Get commissioning parameters */
    mfd_getPasscode(passcode, sizeof(passcode));
    mfd_getDiscriminator(discriminator, sizeof(discriminator));
    printf("Passcode: %s, Discriminator: %u\r\n", passcode,
           (discriminator[0] << 8) | discriminator[1]);
    
    /* Get SPAKE2+ authentication parameters */
    mfd_getSapke2It(spake2_it, sizeof(spake2_it));
    mfd_getSapke2Salt(spake2_salt, sizeof(spake2_salt));
    mfd_getSapke2Verifier(spake2_verifier, sizeof(spake2_verifier));
}
```

### Certificate Chain Verification

```c
#include "bl_mfd.h"
#include <stdio.h>

int verify_device_certificate_chain(void)
{
    uint8_t dac_cert[2048];
    uint8_t pai_cert[2048];
    uint8_t cd[2048];
    int ret;
    
    /* Get the three-layer certificates */
    ret = mfd_getDacCert(dac_cert, sizeof(dac_cert));
    if (ret != 0) {
        printf("Failed to get DAC cert\r\n");
        return -1;
    }
    
    ret = mfd_getPaiCert(pai_cert, sizeof(pai_cert));
    if (ret != 0) {
        printf("Failed to get PAI cert\r\n");
        return -1;
    }
    
    ret = mfd_getCd(cd, sizeof(cd));
    if (ret != 0) {
        printf("Failed to get CD\r\n");
        return -1;
    }
    
    /* Execute certificate chain verification */
    /* Actual verification requires invoking Matter SDK certificate verification APIs */
    printf("Certificate chain retrieved successfully\r\n");
    printf("DAC -> PAI -> CD\r\n");
    
    return 0;
}
```

## Data Storage Structure

MFD data is stored in a specific Flash partition, organized in TLV (Type-Length-Value) format:

| Element ID | Description | Data Type |
|------------|------|----------|
| 0x0001 | DAC Certificate | Certificate |
| 0x0002 | DAC Private Key | Private Key (encrypted) |
| 0x0003 | PAI Certificate | Certificate |
| 0x0004 | CD | Certificate |
| 0x0005 | Passcode | UTF-8 String |
| 0x0006 | Discriminator | Integer |
| 0x0007 | Vendor ID | Integer |
| 0x0008 | Product ID | Integer |
| 0x0009 | Vendor Name | String |
| 0x000A | Product Name | String |
| 0x000B | SPAKE2+ Iterations | Integer |
| 0x000C | SPAKE2+ Salt | Binary |
| 0x000D | SPAKE2+ Verifier | Binary |
| 0x000E | Rotating Device ID Unique ID | Binary |

Data corresponding to any Element ID can be accessed via the `mfd_getElementById()` interface.

## Security Considerations

1. **Private Key Protection**: DAC private keys are stored encrypted in Flash and require Boot2 or security engine cooperation for decryption
2. **Data Integrity**: The factory data area should have integrity protection mechanisms to prevent data tampering
3. **Access Control**: Sensitive data interfaces should have appropriate access permission control
4. **Secure Erasure**: Authentication data should be securely erased when a device leaves the network

## References

- [Matter Protocol Specification](https://csa-iot.org/)
- BL616/BL618 Bouffalo SDK MFD Component
  - `components/wireless/matter/mfd/include/bl_mfd.h`
  - `components/wireless/matter/mfd/bl_mfd_bl616.h`
