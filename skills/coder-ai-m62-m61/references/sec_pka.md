# PKA API Reference (BL616/BL618)

> **Source:** `bouffalo_sdk/drivers/lhal/include/bflb_sec_pka.h`  
> **Mutex Header:** `bouffalo_sdk/drivers/lhal/include/bflb_sec_mutex.h`

## Overview

The PKA (Public Key Accelerator) is a hardware accelerator for large-number arithmetic and modular operations used in public-key cryptography. It supports operations up to 4096-bit (512-byte) operands via a register-based programming model.

The PKA hardware provides two categories of operations:

- **Large Number (L) operations:** Basic arithmetic on arbitrary-length integers (add, sub, mul, div, sqr, cmp, shift by 2^n).
- **Modular (M) operations:** Arithmetic modulo a prime or modulus N (modular add, sub, mul, sqr, exp, inv, rem).

## Register Size Macros

The PKA operates on 32-bit word-aligned data. Register sizes are specified as total byte size:

| Macro | Value | Bytes | 32-bit Words | Typical Use |
|-------|-------|-------|-------------|-------------|
| `SEC_ENG_PKA_REG_SIZE_8` | 1 | 8 | 2 | Small keys |
| `SEC_ENG_PKA_REG_SIZE_16` | 2 | 16 | 4 | |
| `SEC_ENG_PKA_REG_SIZE_32` | 3 | 32 | 8 | ECC P-256 operands |
| `SEC_ENG_PKA_REG_SIZE_64` | 4 | 64 | 16 | |
| `SEC_ENG_PKA_REG_SIZE_96` | 5 | 96 | 24 | |
| `SEC_ENG_PKA_REG_SIZE_128` | 6 | 128 | 32 | RSA-1024 |
| `SEC_ENG_PKA_REG_SIZE_192` | 7 | 192 | 48 | RSA-1536 |
| `SEC_ENG_PKA_REG_SIZE_256` | 8 | 256 | 64 | RSA-2048 |
| `SEC_ENG_PKA_REG_SIZE_384` | 9 | 384 | 96 | RSA-3072 |
| `SEC_ENG_PKA_REG_SIZE_512` | 10 | 512 | 128 | RSA-4096 |

## Operation Opcodes

These opcodes are used internally by the PKA hardware. The API functions abstract them away, but they are useful for understanding the hardware capabilities:

### Large Number Operations

| Macro | Opcode | Description |
|-------|--------|-------------|
| `SEC_ENG_PKA_OP_LMOD2N` | `0x11` | Large modulo 2ⁿ (mask lower n bits) |
| `SEC_ENG_PKA_OP_LDIV2N` | `0x12` | Large divide by 2ⁿ (right shift n bits) |
| `SEC_ENG_PKA_OP_LMUL2N` | `0x13` | Large multiply by 2ⁿ (left shift n bits) |
| `SEC_ENG_PKA_OP_LDIV` | `0x14` | Large division |
| `SEC_ENG_PKA_OP_LSQR` | `0x15` | Large square |
| `SEC_ENG_PKA_OP_LMUL` | `0x16` | Large multiply |
| `SEC_ENG_PKA_OP_LSUB` | `0x17` | Large subtraction |
| `SEC_ENG_PKA_OP_LADD` | `0x18` | Large addition |
| `SEC_ENG_PKA_OP_LCMP` | `0x19` | Large compare |

### Modular Operations

| Macro | Opcode | Description |
|-------|--------|-------------|
| `SEC_ENG_PKA_OP_MDIV2` | `0x21` | Modular divide by 2 |
| `SEC_ENG_PKA_OP_MINV` | `0x22` | Modular inverse |
| `SEC_ENG_PKA_OP_MEXP` | `0x23` | Modular exponentiation |
| `SEC_ENG_PKA_OP_MSQR` | `0x24` | Modular square |
| `SEC_ENG_PKA_OP_MMUL` | `0x25` | Modular multiply |
| `SEC_ENG_PKA_OP_MREM` | `0x26` | Modular remainder |
| `SEC_ENG_PKA_OP_MSUB` | `0x27` | Modular subtraction |
| `SEC_ENG_PKA_OP_MADD` | `0x28` | Modular addition |

### Data Movement / Control Operations

| Macro | Opcode | Description |
|-------|--------|-------------|
| `SEC_ENG_PKA_OP_RESIZE` | `0x31` | Resize register |
| `SEC_ENG_PKA_OP_MOVDAT` | `0x32` | Move data between registers |
| `SEC_ENG_PKA_OP_NLIR` | `0x33` | Load to register (non-last) |
| `SEC_ENG_PKA_OP_SLIR` | `0x34` | Load immediate (small, single word) |
| `SEC_ENG_PKA_OP_CLIR` | `0x35` | Clear register |
| `SEC_ENG_PKA_OP_CFLIRI_BUFFER` | `0x36` | Clear then load immediate from buffer |
| `SEC_ENG_PKA_OP_CTLIRI_PLD` | `0x37` | Clear then load immediate to payload |
| `SEC_ENG_PKA_OP_CFLIR_BUFFER` | `0x38` | Clear then load from buffer |
| `SEC_ENG_PKA_OP_CTLIR_PLD` | `0x39` | Clear then load to payload |

---

## LHAL API Functions

### Lifecycle

#### bflb_pka_init

Initialize the PKA hardware accelerator.

```c
void bflb_pka_init(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | PKA device handle |

---

#### bflb_pka_deinit

Deinitialize the PKA hardware accelerator.

```c
void bflb_pka_deinit(struct bflb_device_s *dev);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | PKA device handle |

---

### Large Number Operations (L-Ops)

Large number operations work on arbitrary-precision integers. They do NOT involve a modulus.

#### bflb_pka_ladd

Large addition: `D = S0 + S1`

```c
void bflb_pka_ladd(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s1_regindex,
                   uint8_t s1_regsize,
                   uint8_t lastop);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | PKA device handle |
| `s0_regindex` | `uint8_t` | Source operand 0 register index |
| `s0_regsize` | `uint8_t` | Source operand 0 register size (see Register Size Macros) |
| `d0_regindex` | `uint8_t` | Destination register index (result) |
| `d0_regsize` | `uint8_t` | Destination register size |
| `s1_regindex` | `uint8_t` | Source operand 1 register index |
| `s1_regsize` | `uint8_t` | Source operand 1 register size |
| `lastop` | `uint8_t` | Set to 1 for the last operation in a sequence, 0 otherwise |

---

#### bflb_pka_lsub

Large subtraction: `D = S0 - S1`

```c
void bflb_pka_lsub(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s1_regindex,
                   uint8_t s1_regsize,
                   uint8_t lastop);
```

Parameters same as `bflb_pka_ladd`.

---

#### bflb_pka_lmul

Large multiplication: `D = S0 × S1`

```c
void bflb_pka_lmul(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s1_regindex,
                   uint8_t s1_regsize,
                   uint8_t lastop);
```

Parameters same as `bflb_pka_ladd`.

---

#### bflb_pka_lsqr

Large square: `D = S0²`

```c
void bflb_pka_lsqr(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t lastop);
```

---

#### bflb_pka_ldiv

Large division: `D = S0 / S1` (quotient), remainder stored in S2 register space.

```c
void bflb_pka_ldiv(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s2_regindex,
                   uint8_t s2_regsize,
                   uint8_t lastop);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `s2_regindex` | `uint8_t` | Remainder register index (S2 = S0 mod S1) |
| `s2_regsize` | `uint8_t` | Remainder register size |

---

#### bflb_pka_lcmp

Large compare: returns 0 if S0 == S1, non-zero otherwise.

```c
uint8_t bflb_pka_lcmp(struct bflb_device_s *dev,
                      uint8_t s0_regindex,
                      uint8_t s0_regsize,
                      uint8_t s1_regindex,
                      uint8_t s1_regsize);
```

**Returns:** Comparison result (0 if equal)

---

#### bflb_pka_lmod2n

Modulo 2ⁿ: `D = S0 mod 2^bit_shift` (masks lower N bits).

```c
void bflb_pka_lmod2n(struct bflb_device_s *dev,
                     uint8_t s0_regindex,
                     uint8_t s0_regsize,
                     uint8_t d0_regindex,
                     uint8_t d0_regsize,
                     uint16_t bit_shift,
                     uint8_t lastop);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `bit_shift` | `uint16_t` | Number of bits N for the 2ⁿ modulus |

---

#### bflb_pka_ldiv2n

Divide by 2ⁿ (right shift): `D = S0 / 2^bit_shift`

```c
void bflb_pka_ldiv2n(struct bflb_device_s *dev,
                     uint8_t s0_regindex,
                     uint8_t s0_regsize,
                     uint8_t d0_regindex,
                     uint8_t d0_regsize,
                     uint16_t bit_shift,
                     uint8_t lastop);
```

---

#### bflb_pka_lmul2n

Multiply by 2ⁿ (left shift): `D = S0 × 2^bit_shift`

```c
void bflb_pka_lmul2n(struct bflb_device_s *dev,
                     uint8_t s0_regindex,
                     uint8_t s0_regsize,
                     uint8_t d0_regindex,
                     uint8_t d0_regsize,
                     uint16_t bit_shift,
                     uint8_t lastop);
```

---

### Modular Operations (M-Ops)

Modular operations compute results modulo N. The modulus N must be preloaded into the register at index 2.

#### bflb_pka_madd

Modular addition: `D = (S0 + S1) mod N`

```c
void bflb_pka_madd(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s1_regindex,
                   uint8_t s1_regsize,
                   uint8_t s2_regindex,
                   uint8_t s2_regsize,
                   uint8_t lastop);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | PKA device handle |
| `s0_regindex` | `uint8_t` | Source operand 0 register index |
| `s0_regsize` | `uint8_t` | Source operand 0 register size |
| `d0_regindex` | `uint8_t` | Destination register index (result) |
| `d0_regsize` | `uint8_t` | Destination register size |
| `s1_regindex` | `uint8_t` | Source operand 1 register index |
| `s1_regsize` | `uint8_t` | Source operand 1 register size |
| `s2_regindex` | `uint8_t` | Modulus N register index |
| `s2_regsize` | `uint8_t` | Modulus N register size |
| `lastop` | `uint8_t` | Set to 1 for the last operation in a sequence |

---

#### bflb_pka_msub

Modular subtraction: `D = (S0 - S1) mod N`

```c
void bflb_pka_msub(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s1_regindex,
                   uint8_t s1_regsize,
                   uint8_t s2_regindex,
                   uint8_t s2_regsize,
                   uint8_t lastop);
```

Parameters same as `bflb_pka_madd`.

---

#### bflb_pka_mmul

Modular multiplication: `D = (S0 × S1) mod N`

```c
void bflb_pka_mmul(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s1_regindex,
                   uint8_t s1_regsize,
                   uint8_t s2_regindex,
                   uint8_t s2_regsize,
                   uint8_t lastop);
```

Parameters same as `bflb_pka_madd`.

---

#### bflb_pka_msqr

Modular square: `D = (S0²) mod N`

```c
void bflb_pka_msqr(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s2_regindex,
                   uint8_t s2_regsize,
                   uint8_t lastop);
```

---

#### bflb_pka_mexp

Modular exponentiation: `D = (S0 ^ S1) mod S2`

```c
void bflb_pka_mexp(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s1_regindex,
                   uint8_t s1_regsize,
                   uint8_t s2_regindex,
                   uint8_t s2_regsize,
                   uint8_t lastop);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `s0_regindex` | `uint8_t` | Base register index |
| `s1_regindex` | `uint8_t` | Exponent register index |
| `s2_regindex` | `uint8_t` | Modulus N register index |

---

#### bflb_pka_minv

Modular inverse: `D = S0⁻¹ mod S2`

```c
void bflb_pka_minv(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s2_regindex,
                   uint8_t s2_regsize,
                   uint8_t lastop);
```

---

#### bflb_pka_mrem

Modular remainder: `D = S0 mod S2`

```c
void bflb_pka_mrem(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t s2_regindex,
                   uint8_t s2_regsize,
                   uint8_t lastop);
```

---

### Register Data Operations

#### bflb_pka_write

Write data from a RAM buffer into a PKA register.

```c
void bflb_pka_write(struct bflb_device_s *dev,
                    uint8_t regindex,
                    uint8_t regsize,
                    const uint32_t *data,
                    uint16_t size,
                    uint8_t lastop);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | PKA device handle |
| `regindex` | `uint8_t` | Target register index |
| `regsize` | `uint8_t` | Register size (use `SEC_ENG_PKA_REG_SIZE_*`) |
| `data` | `const uint32_t *` | Pointer to source data buffer (32-bit aligned, little-endian) |
| `size` | `uint16_t` | Number of bytes to write |
| `lastop` | `uint8_t` | Set to 1 if this is the last operation in a chain |

---

#### bflb_pka_read

Read data from a PKA register into a RAM buffer.

```c
void bflb_pka_read(struct bflb_device_s *dev,
                   uint8_t regindex,
                   uint8_t regsize,
                   uint32_t *data,
                   uint16_t size);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | PKA device handle |
| `regindex` | `uint8_t` | Source register index |
| `regsize` | `uint8_t` | Register size |
| `data` | `uint32_t *` | Destination buffer (32-bit aligned) |
| `size` | `uint16_t` | Number of bytes to read |

---

#### bflb_pka_regsize

Resize a register (change the size of a register).

```c
void bflb_pka_regsize(struct bflb_device_s *dev,
                      uint8_t s0_regindex,
                      uint8_t s0_regsize,
                      uint8_t d0_regindex,
                      uint8_t d0_regsize,
                      uint8_t lastop);
```

---

#### bflb_pka_movdat

Move data between PKA registers.

```c
void bflb_pka_movdat(struct bflb_device_s *dev,
                     uint8_t s0_regindex,
                     uint8_t s0_regsize,
                     uint8_t d0_regindex,
                     uint8_t d0_regsize,
                     uint8_t lastop);
```

---

#### bflb_pka_slir

Small load immediate — load a single 32-bit immediate value into a register.

```c
void bflb_pka_slir(struct bflb_device_s *dev,
                   uint8_t regindex,
                   uint8_t regsize,
                   uint32_t data,
                   uint8_t lastop);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `regindex` | `uint8_t` | Target register index |
| `regsize` | `uint8_t` | Register size |
| `data` | `uint32_t` | 32-bit immediate value to load |
| `lastop` | `uint8_t` | Set to 1 for last operation |

---

#### bflb_pka_nlir

Load data from buffer to register (non-last immediate register load).

```c
void bflb_pka_nlir(struct bflb_device_s *dev,
                   uint8_t s0_regindex,
                   uint8_t s0_regsize,
                   uint8_t d0_regindex,
                   uint8_t d0_regsize,
                   uint8_t lastop);
```

---

#### bflb_pka_clir

Clear a register (set all bytes to zero).

```c
void bflb_pka_clir(struct bflb_device_s *dev,
                   uint8_t regindex,
                   uint8_t regsize,
                   uint16_t size,
                   uint8_t lastop);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `regindex` | `uint8_t` | Register index to clear |
| `regsize` | `uint8_t` | Register size |
| `size` | `uint16_t` | Number of bytes to clear |
| `lastop` | `uint8_t` | Set to 1 for last operation |

---

### Montgomery Conversion

The PKA uses Montgomery form internally for efficient modular arithmetic. These functions convert between standard (GF) representation and Montgomery form.

#### bflb_pka_gf2mont

Convert a value from GF (standard) representation to Montgomery form.

```c
void bflb_pka_gf2mont(struct bflb_device_s *dev,
                      uint8_t s_regindex,
                      uint8_t s_regsize,
                      uint8_t d_regindex,
                      uint8_t d_regsize,
                      uint8_t t_regindex,
                      uint8_t t_regsize,
                      uint8_t p_regindex,
                      uint8_t p_regsize,
                      uint32_t size);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | PKA device handle |
| `s_regindex` | `uint8_t` | Source register (GF value) |
| `s_regsize` | `uint8_t` | Source register size |
| `d_regindex` | `uint8_t` | Destination register (Montgomery result) |
| `d_regsize` | `uint8_t` | Destination register size |
| `t_regindex` | `uint8_t` | Temporary register index |
| `t_regsize` | `uint8_t` | Temporary register size |
| `p_regindex` | `uint8_t` | Modulus P register index |
| `p_regsize` | `uint8_t` | Modulus P register size |
| `size` | `uint32_t` | Operand size in bytes |

---

#### bflb_pka_mont2gf

Convert a value from Montgomery form back to GF (standard) representation.

```c
void bflb_pka_mont2gf(struct bflb_device_s *dev,
                      uint8_t s_regindex,
                      uint8_t s_regsize,
                      uint8_t d_regindex,
                      uint8_t d_regsize,
                      uint8_t invt_regindex,
                      uint8_t invt_regsize,
                      uint8_t t_regindex,
                      uint8_t t_regsize,
                      uint8_t p_regindex,
                      uint8_t p_regsize);
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dev` | `struct bflb_device_s *` | PKA device handle |
| `s_regindex` | `uint8_t` | Source register (Montgomery value) |
| `s_regsize` | `uint8_t` | Source register size |
| `d_regindex` | `uint8_t` | Destination register (GF result) |
| `d_regsize` | `uint8_t` | Destination register size |
| `invt_regindex` | `uint8_t` | Inverse-R register index (precomputed) |
| `invt_regsize` | `uint8_t` | Inverse-R register size |
| `t_regindex` | `uint8_t` | Temporary register index |
| `t_regsize` | `uint8_t` | Temporary register size |
| `p_regindex` | `uint8_t` | Modulus P register index |
| `p_regsize` | `uint8_t` | Modulus P register size |

---

### Mutex (Thread Safety)

The PKA is a shared hardware resource. The SDK provides mutex functions for thread-safe access. These are declared in `bflb_sec_mutex.h`:

```c
int bflb_sec_pka_mutex_take(void);
int bflb_sec_pka_mutex_give(void);
```

**Usage:**

```c
bflb_sec_pka_mutex_take();
// ... PKA operations ...
bflb_sec_pka_mutex_give();
```

---

## Register Layout

The PKA hardware provides multiple general-purpose registers indexed from 0 upward. Each register can hold up to 512 bytes (128 words). The mapping of register indices is:

| Register Index | Typical Use |
|:--------------:|-------------|
| 0 | Modulus N, general operand |
| 1 | N-Prime, general operand |
| 2 | InvR-N, modulus for modular ops |
| 3 | N-Prime-P, temp, general operand |
| 4 | InvR-P, temp, general operand |
| 5+ | General-purpose (used by applications) |

---

## Usage Examples

### Example 1: Modular Exponentiation (RSA)

```c
#include "bflb_sec_pka.h"
#include "bflb_sec_mutex.h"

void pka_rsa_exp_example(void)
{
    struct bflb_device_s *pka;

    // Get PKA device handle
    pka = bflb_device_get_by_name("pka");

    // Initialize PKA
    bflb_pka_init(pka);

    // Take mutex for thread safety
    bflb_sec_pka_mutex_take();

    // Step 1: Load base into register 0
    uint32_t base[64];  // 2048-bit value
    // ... fill base with data ...
    bflb_pka_write(pka, 0, SEC_ENG_PKA_REG_SIZE_256, base, 256, 0);

    // Step 2: Load exponent into register 1
    uint32_t exponent[64];
    // ... fill exponent with data ...
    bflb_pka_write(pka, 1, SEC_ENG_PKA_REG_SIZE_256, exponent, 256, 0);

    // Step 3: Load modulus into register 2
    uint32_t modulus[64];
    // ... fill modulus with data ...
    bflb_pka_write(pka, 2, SEC_ENG_PKA_REG_SIZE_256, modulus, 256, 0);

    // Step 4: Perform modular exponentiation
    // D0 = (S0 ^ S1) mod S2
    bflb_pka_mexp(pka,
                  0, SEC_ENG_PKA_REG_SIZE_256,  // S0: base
                  3, SEC_ENG_PKA_REG_SIZE_256,  // D0: result
                  1, SEC_ENG_PKA_REG_SIZE_256,  // S1: exponent
                  2, SEC_ENG_PKA_REG_SIZE_256,  // S2: modulus
                  1);  // lastop=1

    // Step 5: Read result from register 3
    uint32_t result[64];
    bflb_pka_read(pka, 3, SEC_ENG_PKA_REG_SIZE_256, result, 256);

    bflb_sec_pka_mutex_give();
    bflb_pka_deinit(pka);
}
```

### Example 2: ECC Point Operations (secp256r1)

This simplified example demonstrates register layout for ECC operations on the NIST P-256 curve:

```c
void pka_ecc_secp256r1_example(void)
{
    struct bflb_device_s *pka;
    pka = bflb_device_get_by_name("pka");

    bflb_pka_init(pka);
    bflb_sec_pka_mutex_take();

    // Register layout for secp256r1:
    //   Reg 0: Modulus N (order of curve)
    //   Reg 1: Prime N of N  
    //   Reg 2: InvR of N
    //   Reg 3: Prime N of P (field prime)
    //   Reg 4: InvR of P
    //   Reg 5+: Operands

    // Load curve parameters
    bflb_pka_write(pka, 0, SEC_ENG_PKA_REG_SIZE_32, secp256r1_n, 32, 0);
    bflb_pka_write(pka, 1, SEC_ENG_PKA_REG_SIZE_32, secp256r1_prime_n, 32, 0);
    bflb_pka_write(pka, 2, SEC_ENG_PKA_REG_SIZE_32, secp256r1_invr_n, 32, 0);
    bflb_pka_write(pka, 3, SEC_ENG_PKA_REG_SIZE_32, secp256r1_prime_p, 32, 0);
    bflb_pka_write(pka, 4, SEC_ENG_PKA_REG_SIZE_32, secp256r1_invr_p, 32, 1);

    // Load operands into reg 5, 6 and perform modular operations...
    // (actual ECC point multiplication involves many PKA operations)

    bflb_sec_pka_mutex_give();
    bflb_pka_deinit(pka);
}
```

### Example 3: Large Number Arithmetic (without modulus)

```c
void pka_large_number_example(void)
{
    struct bflb_device_s *pka;
    pka = bflb_device_get_by_name("pka");

    bflb_pka_init(pka);
    bflb_sec_pka_mutex_take();

    // Load two 1024-bit numbers
    uint32_t num_a[32], num_b[32];
    // ... fill buffers ...

    // Load into registers
    bflb_pka_write(pka, 0, SEC_ENG_PKA_REG_SIZE_128, num_a, 128, 0);
    bflb_pka_write(pka, 1, SEC_ENG_PKA_REG_SIZE_128, num_b, 128, 1);

    // Multiply: D2 = S0 × S1
    bflb_pka_lmul(pka,
                  0, SEC_ENG_PKA_REG_SIZE_128,  // S0
                  2, SEC_ENG_PKA_REG_SIZE_256,  // D0 (needs double size)
                  1, SEC_ENG_PKA_REG_SIZE_128,  // S1
                  1);  // lastop=1

    // Read 2048-bit product
    uint32_t product[64];
    bflb_pka_read(pka, 2, SEC_ENG_PKA_REG_SIZE_256, product, 256);

    bflb_sec_pka_mutex_give();
    bflb_pka_deinit(pka);
}
```

---

## Important Notes

1. **Thread Safety:** The PKA hardware is a shared resource. Always use `bflb_sec_pka_mutex_take()` / `bflb_sec_pka_mutex_give()` around PKA operations to avoid race conditions.

2. **The `lastop` Parameter:** When chaining multiple operations, set `lastop = 0` for all intermediate operations, and `lastop = 1` only for the final operation. For standalone operations, always set `lastop = 1`.

3. **Register Index 2:** For modular operations (M-ops), register index 2 is used as the modulus N. Ensure the modulus is loaded into this register before performing modular operations.

4. **Data Alignment:** All data buffers passed to `bflb_pka_write()` and `bflb_pka_read()` must be 32-bit (4-byte) aligned. The SDK's `ALIGN4` attribute can enforce this.

5. **Little-Endian:** Data is stored in little-endian byte order in the 32-bit word buffers. The least significant word comes first.

6. **Register Size Matching:** The destination register must be large enough to hold the result. For multiplication, this typically requires double the operand size. For modular operations, the result size should match the modulus size.

7. **Montgomery Domain:** Modular arithmetic on PKA operates in Montgomery domain. Use `bflb_pka_gf2mont()` to convert inputs before operations and `bflb_pka_mont2gf()` to convert results back.

8. **Error Handling:** PKA API functions do not return error codes. It is the caller's responsibility to ensure valid register indices, sizes, and properly initialized device handles.
