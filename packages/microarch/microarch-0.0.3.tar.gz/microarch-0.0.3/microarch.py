#!/usr/bin/env python

#
# Copyright (c) 2019-2022 Knuth Project
#

from enum import Enum
import cpuid
import importlib
from collections import deque

KTH_MARCH_BUILD_VERSION = 1
KTH_MARCH_BUILD_VERSION_BYTES = KTH_MARCH_BUILD_VERSION.to_bytes(2, byteorder='big')
KTH_MARCH_BUILD_VERSION_BITS = list(map(lambda x : int(x) == 1 , bin(KTH_MARCH_BUILD_VERSION_BYTES[0])[2:].zfill(8) + bin(KTH_MARCH_BUILD_VERSION_BYTES[1])[2:].zfill(8)))
KTH_EXTENSIONS_MAX = 256
MIN_EXTENSION = 16

DEFAULT_ORGANIZATION_NAME = 'k-nuth'
DEFAULT_LOGIN_USERNAME = 'fpelliccioni'
DEFAULT_USERNAME = 'kth'
DEFAULT_REPOSITORY = 'kth'

# --------------------------------------------

base94_charset = ''.join(map(chr, range(33,127)))
base58_charset = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'

def base58_flex_encode(val, chrset=base58_charset):
    """\
    Returns a value encoded using 'chrset' regardless of length and
    composition... well, needs 2 printable asccii chars minimum...

    :param val: base-10 integer value to encode as base*
    :param chrset: the characters to use for encoding

    Note: While this could encrypt some value, it is an insecure toy.

    """
    basect = len(chrset)
    assert basect > 1
    encode = deque()

    while val > 0:
        val, mod = divmod(val, basect)
        encode.appendleft(chrset[mod])

    return ''.join(encode)

def base58_flex_decode(enc, chrset=base58_charset):
    """\
    Returns the 'chrset'-decoded value of 'enc'. Of course this needs to use
    the exact same charset as when to encoding the value.

    :param enc: base-* encoded value to decode
    :param chrset: the character-set used for original encoding of 'enc' value

    Note: Did you read the 'encode' note above? Splendid, now have
             some fun... somewhere...

    """
    basect = len(chrset)
    decoded = 0

    for e, c in enumerate(enc[::-1]):
        decoded += ((basect**e) * chrset.index(c))

    return decoded

# --------------------------------------------

def adjust_compiler_name(os, compiler):
    if os == "Windows" and compiler == "gcc":
        return "mingw"
    if compiler == "Visual Studio":
        return "msvc"

    return compiler

# --------------

# def reserved():
#     return False

def max_function_id():
	a, _, _, _ = cpuid.cpuid(0)
	return a

def max_extended_function():
	a, _, _, _ = cpuid.cpuid(0x80000000)
	return a

def support_long_mode():
    if max_extended_function() < 0x80000001: return False
    _, _, _, d = cpuid.cpuid(0x80000001)
    return (d & (1 << 29)) != 0

# Level 1 Features (baseline) ------------------------------------------
def support_cmov():
    # return CPU_Rep.f_1_EDX_[15];
    if max_function_id() < 0x00000001: return False
    _, _, _, d = cpuid.cpuid(0x00000001)
    return d & (1 << 15) != 0

def support_cx8():
    # cmpxchg8b
    # return CPU_Rep.f_1_EDX_[8];
    if max_function_id() < 0x00000001: return False
    _, _, _, d = cpuid.cpuid(0x00000001)
    return d & (1 << 8) != 0

def support_fpu():
    # X87 - floating-point-unit
    if max_function_id() < 0x00000001: return False
    _, _, _, d = cpuid.cpuid(0x00000001)
    return d & (1 << 0) != 0

def support_fxsr():
    # fxsave
    if max_function_id() < 0x00000001: return False
    _, _, _, d = cpuid.cpuid(0x00000001)
    return d & (1 << 24) != 0

def support_mmx():
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L851
    if max_function_id() < 0x00000001: return False
    _, _, _, d = cpuid.cpuid(0x00000001)
    return d & (1 << 23) != 0

# support_osfxsr:
#   Operating system support for FXSAVE and FXRSTOR instructions
#   https://en.wikipedia.org/wiki/Control_register
#   https://www.felixcloutier.com/x86/fxsave


# support_sce
#   Operating system check

def support_syscall():
    if max_extended_function() < 0x80000001: return False
    _, _, _, d = cpuid.cpuid(0x80000001)
    return d & (1 << 11) != 0

def support_sse():
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L857
    if max_function_id() < 0x00000001: return False
    _, _, _, d = cpuid.cpuid(0x00000001)
    return d & (1 << 25) != 0

def support_sse2():
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L860
    if max_function_id() < 0x00000001: return False
    _, _, _, d = cpuid.cpuid(0x00000001)
    return d & (1 << 26) != 0

def support_level1_features():
    return support_long_mode() and \
        support_cmov() and \
        support_cx8() and \
        support_fpu() and \
        support_fxsr() and \
        support_mmx() and \
        support_sse() and \
        support_sse2()

        # TODO(fernando): missing OSFXSR and SCE
        # Check what to do

# Level 2 Features - x86-64-v2 ------------------------------------------

# CMPXCHG16B
def support_cx16():
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return c & (1 << 13) != 0

def support_lahf_sahf():
    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return c & (1 << 0) != 0

def support_popcnt():
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L884
    if support_abm(): return True

    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return c & (1 << 23) != 0

def support_sse3():
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L863
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return c & (1 << 0) != 0

def support_sse41():
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L872
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    # return c & 0x00080000 != 0
    return c & (1 << 19) != 0

def support_sse42():
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L875
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    # return c & 0x00100000 != 0
    return c & (1 << 20) != 0

def support_ssse3():
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L869
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    # return c & 0x00000200 != 0
    return c & (1 << 9) != 0

def support_level2_features():
    return support_cx16() and \
            support_lahf_sahf() and \
            support_popcnt() and \
            support_sse3() and \
            support_sse41() and \
            support_sse42() and \
            support_ssse3()


# Level 3 Features - x86-64-v3 ------------------------------------------

def support_avx_cpu():
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return (c & (1 << 28)) != 0

def support_avx2_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 5)) != 0

# 0000_0007h (ECX=0) EBX[3]
def support_bmi1():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 3)) != 0

# 0000_0007h (ECX=0) EBX[8]
def support_bmi2():
    # if not support_bmi1(): return False           # TODO(fernando)
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 8)) != 0

def support_f16c():
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return (c & (1 << 29)) != 0

def support_fma3_cpu():
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return (c & (1 << 12)) != 0

def support_abm():                  #lzcnt and popcnt on AMD
    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return (c & (1 << 5)) != 0

def support_lzcnt():
    return support_abm()

def support_movbe():
    # CPUID.01H:ECX.MOVBE[bit 22]
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return c & (1 << 22) != 0

# XSAVE family
# XSAVE/XRSTOR, XSETBV/XGETBV and XCR0.
def support_xsave_cpu():
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return (c & (1 << 26)) != 0

def support_level3_features():
    return support_avx_cpu() and \
        support_avx2_cpu() and \
        support_bmi1() and \
        support_bmi2() and \
        support_f16c() and \
        support_fma3_cpu() and \
        support_lzcnt() and \
        support_movbe() and \
        support_xsave_cpu()

    # TODO(fernando): has some of CPU only checks.
    # See what to do


# Level 4 Features - x86-64-v4 ------------------------------------------

# AVX-512 Foundation
def support_avx512f_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 16)) != 0

# AVX-512 Byte and Word Instructions
def support_avx512bw_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 30)) != 0

# AVX-512 Conflict Detection Instructions
def support_avx512cd_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 28)) != 0

# AVX-512 Doubleword and Quadword Instructions
def support_avx512dq_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 17)) != 0

# AVX-512 Vector Length Extensions
def support_avx512vl_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 31)) != 0

def support_level4_features():
    return support_avx512f_cpu() and \
        support_avx512bw_cpu() and \
        support_avx512cd_cpu() and \
        support_avx512dq_cpu() and \
        support_avx512vl_cpu()

    # TODO(fernando): has some of CPU only checks.
    # See what to do

# Other Features ------------------------------------------

# Extended MMX (AMD): intersection of Enhanced 3DNow! (3dnowext) and SSE instruction sets
#   https://en.wikipedia.org/wiki/Extended_MMX
# It is kept as a historical reference. Nowadays it doesn't make sense to check anymore
#   because it has generally been superseded by processors with SSE support.
def support_mmxext():                                                   # No compiler support
    if max_extended_function() < 0x80000001: return False
    _, _, _, d = cpuid.cpuid(0x80000001)
    return d & (1 << 22) != 0

def support_sse4a():
    # CPUID.80000001H:ECX.SSE4A[Bit 6]
    # https://github.com/klauspost/cpuid/blob/master/cpuid.go#L1022
    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return c & (1 << 6) != 0

def support_pku():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 3)) != 0

# PCLMULQDQ
# CLMUL
# https://en.wikipedia.org/wiki/CLMUL_instruction_set
def support_pclmul():
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return (c & (1 << 1)) != 0

def support_fsgsbase():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 0)) != 0

# RDRAND
def support_rdrnd():
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return (c & (1 << 30)) != 0

# 4 operands fused multiply-add
# Just on AMD Bulldozer. Removed from AMD Zen.
def support_fma4_cpu():
    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return (c & (1 << 16)) != 0

# XOP (eXtended Operations)
# Just on AMD Bulldozer. Removed from AMD Zen.
# https://en.wikipedia.org/wiki/XOP_instruction_set
def support_xop_cpu():
    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return c & (1 << 11) != 0

# 8000_0001h ECX[21] TBM
# static bool TBM(void) { return CPU_Rep.isAMD_ && CPU_Rep.f_81_ECX_[21]; }
# https://en.wikipedia.org/wiki/X86_Bit_manipulation_instruction_set#TBM
# Just on AMD, removed from AMD Zen
def support_tbm():
    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return (c & (1 << 21)) != 0

def support_rdseed():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 18)) != 0

# https://en.wikipedia.org/wiki/Intel_ADX
def support_adx():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 19)) != 0

def support_3dnow():
    if max_extended_function() < 0x80000001: return False
    _, _, _, d = cpuid.cpuid(0x80000001)
    return d & (1 << 31) != 0

# enhanced 3DNow!
def support_3dnowext():                                 # GCC flag: -m3dnowa
    if max_extended_function() < 0x80000001: return False
    _, _, _, d = cpuid.cpuid(0x80000001)
    return d & (1 << 30) != 0


# https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-instruction-set-reference-manual-325383.pdf
# pag. 202
# https://www.amd.com/system/files/TechDocs/24594.pdf
# pag. 74
# https://superuser.com/questions/931742/windows-10-64-bit-requirements-does-my-cpu-support-cmpxchg16b-prefetchw-and-la

# Intel:    ECX[8]                              - PREFETCHW
# AMD:      ECX[8], EDX[29], or EDX[31]         - PREFETCH and PREFETCHW
def support_prefetchw():                        # GCC flag: -mprfchw
    if vendorID() == Vendor.AMD and (support_long_mode() or support_3dnow()):
        return True

    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return (c & (1 << 8)) != 0

def support_prefetchwt1():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 0)) != 0

def support_clflushopt():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 23)) != 0

# XSAVE family
def support_xsaveopt_cpu():
    if max_function_id() < 0x0000000D: return False
    a, _, _, _ = cpuid.cpuid_count(0x0000000D, 1)
    return (a & (1 << 0)) != 0

def support_xsavec_cpu():
    if max_function_id() < 0x0000000D: return False
    a, _, _, _ = cpuid.cpuid_count(0x0000000D, 1)
    return (a & (1 << 1)) != 0

# XGETBV with ECX=1 support
def support_xgetbv_ecx1_cpu():                              # No compiler support (yet)
    if max_function_id() < 0x0000000D: return False
    a, _, _, _ = cpuid.cpuid_count(0x0000000D, 1)
    return (a & (1 << 2)) != 0

# XSAVES and XRSTORS instructions
def support_xsaves_cpu():
    if max_function_id() < 0x0000000D: return False
    a, _, _, _ = cpuid.cpuid_count(0x0000000D, 1)
    return (a & (1 << 3)) != 0

def support_clwb():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 24)) != 0

def support_umip():                                         # No compiler support (yet)
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 2)) != 0

# https://hjlebbink.github.io/x86doc/html/PTWRITE.html
def support_ptwrite():
    # If CPUID.(EAX=14H, ECX=0):EBX.PTWRITE [Bit 4] = 0.
    # If LOCK prefix is used.
    # If 66H prefix is used.
    if max_function_id() < 0x00000014: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000014, 0)
    return (b & (1 << 4)) != 0

def support_rdpid():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 22)) != 0

# Software Guard Extensions
def support_sgx():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 2)) != 0

# SGX Launch Configuration
def support_sgx_lc():                                       # No compiler support (yet)
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 30)) != 0

# Galois Field instructions
def support_gfni():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 8)) != 0

# CLMUL instruction set (VEX-256/EVEX)
def support_vpclmulqdq():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 10)) != 0

# Platform configuration (Memory Encryption Technologies Instructions)
def support_pconfig():
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 18)) != 0

# WBNOINVD instruction
def support_wbnoinvd():
    if max_extended_function() < 0x80000008: return False
    _, b, _, _ = cpuid.cpuid(0x80000008)
    return (b & (1 << 9)) != 0

# Move Doubleword as Direct Store
# https://www.felixcloutier.com/x86/movdiri
def support_movdiri():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 27)) != 0

# Move 64 Bytes as Direct Store
def support_movdir64b():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 28)) != 0

# Light Weight Profiling
def support_lwp():
    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return c & (1 << 15) != 0

# MONITOR and MWAIT instructions (SSE3)
# -mmwait
# This option enables built-in functions __builtin_ia32_monitor, and __builtin_ia32_mwait to generate the monitor and mwait machine instructions.
# def support_mwait():
#     if max_function_id() < 0x00000001: return False
#     _, _, c, _ = cpuid.cpuid(0x00000001)
#     return c & (1 << 3) != 0

# MONITORX and MWAITX instructions
# https://reviews.llvm.org/rL269911
def support_mwaitx():
    if max_extended_function() < 0x80000001: return False
    _, _, c, _ = cpuid.cpuid(0x80000001)
    return c & (1 << 29) != 0

# CLZERO instruction
# https://patchew.org/QEMU/20190925214948.22212-1-bigeasy@linutronix.de/
def support_clzero():
    if max_extended_function() < 0x80000008: return False
    _, b, _, _ = cpuid.cpuid(0x80000008)
    return (b & (1 << 0)) != 0

# MCOMMIT instruction
# https://www.amd.com/system/files/TechDocs/24594.pdf
# 8000_0008 EBX[8]
def support_mcommit():                                                  # No compiler support (yet)
    if max_extended_function() < 0x80000008: return False
    _, b, _, _ = cpuid.cpuid(0x80000008)
    return (b & (1 << 8)) != 0

# https://www.amd.com/system/files/TechDocs/24594.pdf
# 8000_0008 EBX[4]
def support_rdpru():                                                    # No compiler support (yet)
    if max_extended_function() < 0x80000008: return False
    _, b, _, _ = cpuid.cpuid(0x80000008)
    return (b & (1 << 4)) != 0

# INVPCID instruction
# PCID - Process Context Identifiers
#    INVPCID - Invalidate TLB entry(s) in a specified PCID
# https://www.amd.com/system/files/TechDocs/24594.pdf
# 0000_0007_0 EBX[10]
def support_invpcid():                                                  # No compiler support (yet)
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 10)) != 0

# https://www.amd.com/system/files/TechDocs/24594.pdf
# 8000_0008 EBX[3]
def support_invlpgb_tlbsync():
    if max_extended_function() < 0x80000008: return False
    _, b, _, _ = cpuid.cpuid(0x80000008)
    return (b & (1 << 3)) != 0

# CET_SS - Control-flow Enforcement Technology / Shadow Stack
# Shadow Stack (Instructions CLRSSBSY, INCSSP, RDSSP, RSTORSSP, SAVEPREVSSP, SETSSBSY, WRSS, WRUSS)
# 0000_0007_0 ECX[7]
def support_cet_ss():                                               # GCC flag -mshstk
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 7)) != 0

# 3rd generation Secure Encrypted Virtualization - Secure Nested Paging
# SNP (Instructions PSMASH, PVALIDATE, RMPADJUST, RMPUPDATE)
# 8000_001F EAX[4]
def support_sev_snp():                                              # No compiler support (yet)
    if max_extended_function() < 0x8000001F: return False
    a, _, _, _ = cpuid.cpuid(0x8000001F)
    return (a & (1 << 4)) != 0

# AVX Vector Neural Network Instructions (VEX encoded)
def support_avxvnni_cpu():                                          # GCC flag -mavxvnni
    if max_function_id() < 0x00000007: return False
    a, _, _, _ = cpuid.cpuid_count(0x00000007, 1)
    return (a & (1 << 4)) != 0

# TSX Restricted Transactional Memory
def support_tsxrtm():                                          # GCC flag -mrtm
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 11)) != 0

# TSX Hardware Lock Elision
def support_tsxhle():                                          # GCC flag -mhle
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 4)) != 0

# Timed pause and user-level monitor/wait
def support_waitpkg():                                          # GCC flag -mwaitpkg
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 5)) != 0

# Enqueue Stores
def support_enqcmd():                                          # GCC flag -menqcmd
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 29)) != 0

# User Interprocessor Interrupts
def support_uintr():                                          # GCC flag -muintr
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 5)) != 0

# TSX suspend load address tracking
def support_tsxldtrk():                                          # GCC flag -mtsxldtrk
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 16)) != 0

# Cache line demote
def support_cldemote():                                          # GCC flag -mcldemote
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 25)) != 0

# Serialize instruction execution
def support_serialize():                                          # GCC flag -mserialize
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 14)) != 0

# HRESET instruction and related MSRs
def support_hreset():                                               # GCC flag -mhreset
    if max_function_id() < 0x00000007: return False
    a, _, _, _ = cpuid.cpuid_count(0x00000007, 1)
    return (a & (1 << 22)) != 0

# # TODO(fernando): ver Enclave en Golang
# def support_enclv():                                      # No compiler support (yet)
#     return False

# Cryptographic Features ------------------------------------------

# AES Native instructions
def support_aes():
    if max_function_id() < 0x00000001: return False
    _, _, c, _ = cpuid.cpuid(0x00000001)
    return (c & (1 << 25)) != 0

# 0000_0007_0 ECX[9]
def support_vaes():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 9)) != 0

def support_sha():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 29)) != 0

# Key Locker
def support_kl():                                               # GCC flag -mkl
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 23)) != 0

# AES Wide Key Locker instructions
def support_widekl():                                          # GCC flag -mwidekl
    if max_function_id() < 0x00000019: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000019, 0)
    return (b & (1 << 2)) != 0



# AVX512 ------------------------------------------

# AVX-512 FP16 Instructions
def support_avx512fp16_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 23)) != 0

# AVX-512 Prefetch Instructions
def support_avx512pf_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 26)) != 0

# AVX-512 Exponential and Reciprocal Instructions
def support_avx512er_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 27)) != 0

# AVX-512 4-register Neural Network Instructions
def support_avx5124vnniw_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 2)) != 0

# AVX-512 4-register Multiply Accumulation Single precision
def support_avx5124fmaps_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 3)) != 0

# AVX-512 Vector Bit Manipulation Instructions
def support_avx512vbmi_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 1)) != 0

# AVX-512 Integer Fused Multiply-Add Instructions
def support_avx512ifma_cpu():
    if max_function_id() < 0x00000007: return False
    _, b, _, _ = cpuid.cpuid_count(0x00000007, 0)
    return (b & (1 << 21)) != 0

# AVX-512 Vector Bit Manipulation Instructions, Version 2
def support_avx512vbmi2_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 6)) != 0

# AVX-512 Vector Population Count Double and Quad-word
def support_avx512vpopcntdq_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 14)) != 0

# AVX-512 Bit Algorithms
def support_avx512bitalg_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 12)) != 0

# AVX-512 Vector Neural Network Instructions
def support_avx512vnni_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
    return (c & (1 << 11)) != 0

# AVX-512 BFLOAT16 Instructions
def support_avx512bf16_cpu():
    if max_function_id() < 0x00000007: return False
    a, _, _, _ = cpuid.cpuid_count(0x00000007, 1)
    return (a & (1 << 5)) != 0

# AVX-512 VP2INTERSECT Doubleword and Quadword Instructions
def support_avx512vp2intersect_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, _,d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 8)) != 0


# AMX (Advanced Matrix Extensions) ------------------------------------------

# https://en.wikipedia.org/wiki/Advanced_Matrix_Extensions

# AMX: Tile computation on bfloat16 numbers
def support_amxbf16_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 22)) != 0

# AMX: Tile architecture
def support_amxtile_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 24)) != 0

# AMX: Tile computation on 8-bit integers
def support_amxint8_cpu():
    if max_function_id() < 0x00000007: return False
    _, _, _, d = cpuid.cpuid_count(0x00000007, 0)
    return (d & (1 << 25)) != 0

# -----------------------------------------------------------------

def version_bit(i):
    global KTH_MARCH_BUILD_VERSION_BITS
    return lambda: KTH_MARCH_BUILD_VERSION_BITS[i]


extensions_map = [
    version_bit(0),
    version_bit(1),
    version_bit(2),
    version_bit(3),
    version_bit(4),
    version_bit(5),
    version_bit(6),
    version_bit(7),

    version_bit(8),
    version_bit(9),
    version_bit(10),
    version_bit(11),
    version_bit(12),
    version_bit(13),
    version_bit(14),
    version_bit(15),

    # 16:
    support_long_mode,         # cpuid._is_long_mode_cpuid,

    # Level 1 (baseline) ------------------------------------------------------------
    # 17:
    support_cmov,
    support_cx8,
    support_fpu,
    support_fxsr,
    support_mmx,
    #  support_osfxsr,      # Operating System check.
    support_syscall,       # System-Call Extension (SCE) Bit           (some part could be related to OS check)
    support_sse,
    support_sse2,

    # Level 2 - x86-64-v2 ------------------------------------------------------------
    support_cx16,
    support_lahf_sahf,
    support_popcnt,
    support_sse3,
    support_sse41,                # SSE4.1
    support_sse42,                # SSE4.2
    support_ssse3,

    # Level 3 - x86-64-v3 ------------------------------------------------------------
    support_avx_cpu,
    support_avx2_cpu,
    support_bmi1,
    support_bmi2,
    support_f16c,
    support_fma3_cpu,
    support_lzcnt,
    support_movbe,

    # TODO(fernando): según el spec de Levels, acá tenemos que chequear OSXSAVE,
    # pero nosotros solo podemos chequear XSAVE a nivel procesador
    # el chequeo de soporte de features del sistema operativo lo debería hacer
    # el nodo en runtime (o quizás no)

    # support_osxsave,
    support_xsave_cpu,

    # Level 4 - x86-64-v4 ------------------------------------------------------------
    support_avx512f_cpu,
    support_avx512bw_cpu,
    support_avx512cd_cpu,
    support_avx512dq_cpu,
    support_avx512vl_cpu,

    # Other Features ------------------------------------------
    support_sse4a,
    support_pku,
    support_pclmul,
    support_fsgsbase,
    support_rdrnd,
    support_fma4_cpu,
    support_xop_cpu,
    support_tbm,
    support_rdseed,
    support_adx,
    support_3dnow,
    support_3dnowext,
    support_prefetchw,
    support_prefetchwt1,
    support_clflushopt,
    support_xsaveopt_cpu,
    support_xsavec_cpu,
    support_xsaves_cpu,
    support_clwb,
    support_ptwrite,
    support_rdpid,
    support_sgx,
    support_gfni,
    support_vpclmulqdq,
    support_pconfig,
    support_wbnoinvd,
    support_movdiri,
    support_movdir64b,
    support_lwp,
    support_mwaitx,
    support_clzero,
    support_invlpgb_tlbsync,
    support_cet_ss,
    support_avxvnni_cpu,
    support_tsxrtm,
    support_tsxhle,
    support_waitpkg,
    support_enqcmd,
    support_uintr,
    support_tsxldtrk,
    support_cldemote,
    support_serialize,
    support_hreset,
    support_aes,
    support_vaes,
    support_sha,
    support_kl,
    support_widekl,
    support_avx512fp16_cpu,
    support_avx512pf_cpu,
    support_avx512er_cpu,
    support_avx5124vnniw_cpu,
    support_avx5124fmaps_cpu,
    support_avx512vbmi_cpu,
    support_avx512ifma_cpu,
    support_avx512vbmi2_cpu,
    support_avx512vpopcntdq_cpu,
    support_avx512bitalg_cpu,
    support_avx512vnni_cpu,
    support_avx512bf16_cpu,
    support_avx512vp2intersect_cpu,
    support_amxbf16_cpu,
    support_amxtile_cpu,
    support_amxint8_cpu,
    support_mmxext,
    support_xgetbv_ecx1_cpu,
    support_umip,
    support_sgx_lc,
    support_mcommit,
    support_rdpru,
    support_invpcid,
    support_sev_snp,
]

extensions_names = [
    None,       # Version Bit 1
    None,       # Version Bit 0
    None,       # Version Bit 1
    None,       # Version Bit 0
    None,       # Version Bit 1
    None,       # Version Bit 0
    None,       # Version Bit 1
    None,       # Version Bit 0

    None,       # Version Bit 1
    None,       # Version Bit 0
    None,       # Version Bit 1
    None,       # Version Bit 0
    None,       # Version Bit 1
    None,       # Version Bit 0
    None,       # Version Bit 1
    None,       # Version Bit 0

    # 16:
    "64 bits",

    # Level 1 (baseline)
    # 17:
    "CMOV",
    "CX8",
    "FPU",
    "FXSR",
    "MMX",
    # "OSFXSR",            # Operating System check.
    "SCE",                 # System-Call Extension (SCE) Bit           (some part could be related to OS check)
    "SSE",
    "SSE2",

    # Level 2 - x86-64-v2
    "CX16",            # CMPXCHG16B
    "LAHF-SAHF",
    "POPCNT",
    "SSE3",
    "SSE4.1",
    "SSE4.2",
    "SSSE3",

    # Level 3 - x86-64-v3
    "AVX",
    "AVX2",
    "BMI1",
    "BMI2",
    "F16C",
    "FMA",
    "LZCNT ABM",
    "MOVBE",
    "XSAVE",             # OSXSAVE     # TODO(fernando): según el spec de Levels, acá tenemos que chequear OSXSAVE,
                                            # pero nosotros solo podemos chequear XSAVE a nivel procesador
                                            # el chequeo de soporte de features del sistema operativo lo debería hacer
                                            # el nodo en runtime (o quizás no)

    # Level 4 - x86-64-v4
    "AVX512F",
    "AVX512BW",
    "AVX512CD",
    "AVX512DQ",
    "AVX512VL",

    # Other Features ------------------------------------------
    "SSE4A",
    "PKU",
    "PCLMUL",
    "FSGSBASE",
    "RDRND",
    "FMA4",
    "XOP",
    "TBM",
    "RDSEED",
    "ADX",
    "3DNOW",
    "3DNOWEXT",
    "PREFETCHW",
    "PREFETCHWT1",
    "CLFLUSHOPT",
    "XSAVEOPT",
    "XSAVEC",
    "XSAVES",
    "CLWB",
    "PTWRITE",
    "RDPID",
    "SGX",
    "GFNI",
    "VPCLMULQDQ",
    "PCONFIG",
    "WBNOINVD",
    "MOVDIRI",
    "MOVDIR64B",
    "LWP",
    "MWAITX",
    "CLZERO",
    "INVLPGB_TLBSYNC",
    "CET_SS",
    "AVXVNNI",
    "TSXRTM",
    "TSXHLE",
    "WAITPKG",
    "ENQCMD",
    "UINTR",
    "TSXLDTRK",
    "CLDEMOTE",
    "SERIALIZE",
    "HRESET",
    "AES",
    "VAES",
    "SHA",
    "KL",
    "WIDEKL",
    "AVX512FP16",
    "AVX512PF",
    "AVX512ER",
    "AVX5124VNNIW",
    "AVX5124FMAPS",
    "AVX512VBMI",
    "AVX512IFMA",
    "AVX512VBMI2",
    "AVX512VPOPCNTDQ",
    "AVX512BITALG",
    "AVX512VNNI",
    "AVX512BF16",
    "AVX512VP2INTERSECT",
    "AMXBF16",
    "AMXTILE",
    "AMXINT8",
    "MMXEXT",
    "XGETBV_ECX1",
    "UMIP",
    "SGX_LC",
    "MCOMMIT",
    "RDPRU",
    "INVPCID",
    "SEV_SNP",
]

extensions_flags = {
    'gcc':         None,
    'apple-clang': None,
    'clang':       None,
    'msvc':        None,
    'mingw':       None
}


# ------------------------------------------------------------------------------------------

extensions_flags['gcc'] = [
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0

    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0

    # Level 0 (64 bits support)
    # 16:
    {'min_version': 5,  'flags': ["-m32", "-m64"]},

    # Level 1 (baseline)
    # 17:
    {'min_version': 5,  'flags': ""},                        # "CMOV"        supported by no flags
    {'min_version': 5,  'flags': ""},                        # "CX8"         supported by no flags
    {'min_version': 5,  'flags': ""},                        # "FPU"         supported by no flags
    {'min_version': 5,  'flags': "-mfxsr"},
    {'min_version': 5,  'flags': "-mmmx"},
    {'min_version': 5,  'flags': ""},                        # "SCE"         supported by no flags
    {'min_version': 5,  'flags': "-msse"},
    {'min_version': 5,  'flags': "-msse2"},

    # Level 2 - x86-64-v2
    {'min_version': 5,  'flags': "-mcx16"},
    {'min_version': 5,  'flags': "-msahf"},
    {'min_version': 5,  'flags': "-mpopcnt"},
    {'min_version': 5,  'flags': "-msse3"},
    {'min_version': 5,  'flags': "-msse4.1"},
    {'min_version': 5,  'flags': "-msse4.2"},
    {'min_version': 5,  'flags': "-mssse3"},

    # Level 3 - x86-64-v3
    {'min_version': 5,  'flags': "-mavx"},
    {'min_version': 5,  'flags': "-mavx2"},
    {'min_version': 5,  'flags': "-mbmi"},
    {'min_version': 5,  'flags': "-mbmi2"},
    {'min_version': 5,  'flags': "-mf16c"},
    {'min_version': 5,  'flags': "-mfma"},
    {'min_version': 5,  'flags': "-mlzcnt -mabm"},          # dual flag
    {'min_version': 5,  'flags': "-mmovbe"},
    {'min_version': 5,  'flags': "-mxsave"},

    # Level 4 - x86-64-v4
    {'min_version': 5,  'flags': "-mavx512f"},
    {'min_version': 5,  'flags': "-mavx512bw"},
    {'min_version': 5,  'flags': "-mavx512cd"},
    {'min_version': 5,  'flags': "-mavx512dq"},
    {'min_version': 5,  'flags': "-mavx512vl"},

    # Other Features ------------------------------------------

    {'min_version': 5,  'flags': "-msse4a"},
    {'min_version': 6,  'flags': "-mpku"},
    {'min_version': 5,  'flags': "-mpclmul"},
    {'min_version': 5,  'flags': "-mfsgsbase"},
    {'min_version': 5,  'flags': "-mrdrnd"},
    {'min_version': 5,  'flags': "-mfma4"},
    {'min_version': 5,  'flags': "-mxop"},
    {'min_version': 5,  'flags': "-mtbm"},
    {'min_version': 5,  'flags': "-mrdseed"},
    {'min_version': 5,  'flags': "-madx"},
    {'min_version': 5,  'flags': "-m3dnow"},
    {'min_version': 7,  'flags': "-m3dnowa"},                    # "3dnowext" enhanced 3DNow!
    {'min_version': 5,  'flags': "-mprfchw"},                    # "prefetchw"
    {'min_version': 5,  'flags': "-mprefetchwt1"},
    {'min_version': 5,  'flags': "-mclflushopt"},
    {'min_version': 5,  'flags': "-mxsaveopt"},
    {'min_version': 5,  'flags': "-mxsavec"},
    {'min_version': 5,  'flags': "-mxsaves"},
    {'min_version': 5,  'flags': "-mclwb"},
    {'min_version': 9,  'flags': "-mptwrite"},
    {'min_version': 7,  'flags': "-mrdpid"},
    {'min_version': 7,  'flags': "-msgx"},
    {'min_version': 8,  'flags': "-mgfni"},
    {'min_version': 8,  'flags': "-mvpclmulqdq"},
    {'min_version': 8,  'flags': "-mpconfig"},
    {'min_version': 8,  'flags': "-mwbnoinvd"},
    {'min_version': 8,  'flags': "-mmovdiri"},
    {'min_version': 8,  'flags': "-mmovdir64b"},
    {'min_version': 5,  'flags': "-mlwp"},
    {'min_version': 5,  'flags': "-mmwaitx"},
    {'min_version': 6,  'flags': "-mclzero"},
    None,                                                         # "invlpgb_tlbsync"         TODO(fernando): y este???? https://www.phoronix.com/news/AMD-Zen-3-Inst-Fixes-GCC11
    {'min_version': 8,  'flags': "-mshstk"},                      # "cet_ss"
    {'min_version': 11, 'flags': "-mavxvnni"},
    {'min_version': 5,  'flags': "-mrtm"},                        # "tsxrtm"
    {'min_version': 5,  'flags': "-mhle"},                        # "tsxhle"
    {'min_version': 9,  'flags': "-mwaitpkg"},
    {'min_version': 10, 'flags': "-menqcmd"},
    {'min_version': 11, 'flags': "-muintr"},
    {'min_version': 11, 'flags': "-mtsxldtrk"},
    {'min_version': 11, 'flags': "-mcldemote"},
    {'min_version': 11, 'flags': "-mserialize"},
    {'min_version': 11, 'flags': "-mhreset"},
    {'min_version': 5,  'flags': "-maes"},
    {'min_version': 8,  'flags': "-mvaes"},
    {'min_version': 5,  'flags': "-msha"},
    {'min_version': 11, 'flags': "-mkl"},
    {'min_version': 11, 'flags': "-mwidekl"},
    {'min_version': 12, 'flags': "-mavx512fp16"},
    {'min_version': 5,  'flags': "-mavx512pf"},
    {'min_version': 5,  'flags': "-mavx512er"},
    {'min_version': 7,  'flags': "-mavx5124vnniw"},
    {'min_version': 7,  'flags': "-mavx5124fmaps"},
    {'min_version': 5,  'flags': "-mavx512vbmi"},
    {'min_version': 5,  'flags': "-mavx512ifma"},
    {'min_version': 8,  'flags': "-mavx512vbmi2"},
    {'min_version': 7,  'flags': "-mavx512vpopcntdq"},
    {'min_version': 8,  'flags': "-mavx512bitalg"},
    {'min_version': 8,  'flags': "-mavx512vnni"},
    {'min_version': 10, 'flags': "-mavx512bf16"},
    {'min_version': 10, 'flags': "-mavx512vp2intersect"},
    {'min_version': 11, 'flags': "-mamx-bf16"},
    {'min_version': 11, 'flags': "-mamx-tile"},
    {'min_version': 11, 'flags': "-mamx-int8"},
    None,                      # "mmxext"
    None,                      # "xgetbv_ecx1"
    None,                      # "umip"
    None,                      # "sgx_lc"
    None,                      # "mcommit"
    None,                      # "rdpru"
    None,                      # "invpcid"
    None,                      # "sev_snp"
]

extensions_flags['clang'] = [
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0

    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0

    # Level 0 (64 bits support)
    # 16:
    {'min_version': 7,  'flags': ["-m32", "-m64"]},

    # Level 1 (baseline)
    # 17:
    {'min_version': 7,  'flags': ""},                        # "CMOV"        supported by no flags
    {'min_version': 7,  'flags': ""},                        # "CX8"         supported by no flags
    {'min_version': 7,  'flags': ""},                        # "FPU"         supported by no flags
    {'min_version': 7,  'flags': "-mfxsr"},
    {'min_version': 7,  'flags': "-mmmx"},
    {'min_version': 7,  'flags': ""},                        # "SCE"         supported by no flags
    {'min_version': 7,  'flags': "-msse"},
    {'min_version': 7,  'flags': "-msse2"},

    # Level 2 - x86-64-v2
    {'min_version': 7,  'flags': "-mcx16"},
    {'min_version': 7,  'flags': "-msahf"},                 # Supported on Clang 6.0.1 but not supported on Clang 6.0.0, so the min Clang version is 7
    {'min_version': 7,  'flags': "-mpopcnt"},
    {'min_version': 7,  'flags': "-msse3"},
    {'min_version': 7,  'flags': "-msse4.1"},
    {'min_version': 7,  'flags': "-msse4.2"},
    {'min_version': 7,  'flags': "-mssse3"},

    # Level 3 - x86-64-v3
    {'min_version': 7,  'flags': "-mavx"},
    {'min_version': 7,  'flags': "-mavx2"},
    {'min_version': 7,  'flags': "-mbmi"},
    {'min_version': 7,  'flags': "-mbmi2"},
    {'min_version': 7,  'flags': "-mf16c"},
    {'min_version': 7,  'flags': "-mfma"},
    {'min_version': 7,  'flags': "-mlzcnt"},          # Clang does not have dual flag -mlzcnt -mabm, it just has -mlzcnt
    {'min_version': 7,  'flags': "-mmovbe"},
    {'min_version': 7,  'flags': "-mxsave"},

    # Level 4 - x86-64-v4
    {'min_version': 7,  'flags': "-mavx512f"},
    {'min_version': 7,  'flags': "-mavx512bw"},
    {'min_version': 7,  'flags': "-mavx512cd"},
    {'min_version': 7,  'flags': "-mavx512dq"},
    {'min_version': 7,  'flags': "-mavx512vl"},

    # Other Features ------------------------------------------

    {'min_version': 7,  'flags': "-msse4a"},
    {'min_version': 7,  'flags': "-mpku"},
    {'min_version': 7,  'flags': "-mpclmul"},
    {'min_version': 7,  'flags': "-mfsgsbase"},
    {'min_version': 7,  'flags': "-mrdrnd"},
    {'min_version': 7,  'flags': "-mfma4"},
    {'min_version': 7,  'flags': "-mxop"},
    {'min_version': 7,  'flags': "-mtbm"},
    {'min_version': 7,  'flags': "-mrdseed"},
    {'min_version': 7,  'flags': "-madx"},
    {'min_version': 7,  'flags': "-m3dnow"},
    {'min_version': 7,  'flags': "-m3dnowa"},                    # "3dnowext" enhanced 3DNow!
    {'min_version': 7,  'flags': "-mprfchw"},                    # "prefetchw"
    {'min_version': 7,  'flags': "-mprefetchwt1"},
    {'min_version': 7,  'flags': "-mclflushopt"},
    {'min_version': 7,  'flags': "-mxsaveopt"},
    {'min_version': 7,  'flags': "-mxsavec"},
    {'min_version': 7,  'flags': "-mxsaves"},
    {'min_version': 7,  'flags': "-mclwb"},
    {'min_version': 7,  'flags': "-mptwrite"},
    {'min_version': 7,  'flags': "-mrdpid"},
    {'min_version': 7,  'flags': "-msgx"},
    {'min_version': 7,  'flags': "-mgfni"},
    {'min_version': 7,  'flags': "-mvpclmulqdq"},
    {'min_version': 7,  'flags': "-mpconfig"},
    {'min_version': 7,  'flags': "-mwbnoinvd"},
    {'min_version': 7,  'flags': "-mmovdiri"},
    {'min_version': 7,  'flags': "-mmovdir64b"},
    {'min_version': 7,  'flags': "-mlwp"},
    {'min_version': 7,  'flags': "-mmwaitx"},
    {'min_version': 7,  'flags': "-mclzero"},
    None,                                                         # "invlpgb_tlbsync"         TODO(fernando): y este???? https://www.phoronix.com/news/AMD-Zen-3-Inst-Fixes-GCC11
    {'min_version': 7,  'flags': "-mshstk"},                      # "cet_ss"
    {'min_version': 12, 'flags': "-mavxvnni"},
    {'min_version': 7,  'flags': "-mrtm"},                        # "tsxrtm"
    None,                                                         # -mhle
    {'min_version': 7,  'flags': "-mwaitpkg"},
    {'min_version': 9,  'flags': "-menqcmd"},
    {'min_version': 12, 'flags': "-muintr"},
    {'min_version': 11, 'flags': "-mtsxldtrk"},
    {'min_version': 7,  'flags': "-mcldemote"},
    {'min_version': 11, 'flags': "-mserialize"},
    {'min_version': 12, 'flags': "-mhreset"},
    {'min_version': 7,  'flags': "-maes"},
    {'min_version': 7,  'flags': "-mvaes"},
    {'min_version': 7,  'flags': "-msha"},
    {'min_version': 12, 'flags': "-mkl"},
    {'min_version': 12, 'flags': "-mwidekl"},
    {'min_version': 14, 'flags': "-mavx512fp16"},
    {'min_version': 7,  'flags': "-mavx512pf"},
    {'min_version': 7,  'flags': "-mavx512er"},
    None,                                                         # -mavx5124vnniw
    None,                                                         # -mavx5124fmaps
    {'min_version': 7,  'flags': "-mavx512vbmi"},
    {'min_version': 7,  'flags': "-mavx512ifma"},
    {'min_version': 7,  'flags': "-mavx512vbmi2"},
    {'min_version': 7,  'flags': "-mavx512vpopcntdq"},
    {'min_version': 7,  'flags': "-mavx512bitalg"},
    {'min_version': 7,  'flags': "-mavx512vnni"},
    {'min_version': 9,  'flags': "-mavx512bf16"},
    {'min_version': 9,  'flags': "-mavx512vp2intersect"},
    {'min_version': 11, 'flags': "-mamx-bf16"},
    {'min_version': 11, 'flags': "-mamx-tile"},
    {'min_version': 11, 'flags': "-mamx-int8"},
    None,                      # "mmxext"
    None,                      # "xgetbv_ecx1"
    None,                      # "umip"
    None,                      # "sgx_lc"
    None,                      # "mcommit"
    None,                      # "rdpru"
    None,                      # "invpcid"
    None,                      # "sev_snp"
]

extensions_flags['apple-clang'] = [
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0

    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0
    None,                        # Version Bit 1
    None,                        # Version Bit 0

    # Level 0 (64 bits support)
    # 16:
    {'min_version': 13, 'flags': ["-m32", "-m64"]},

    # Level 1 (baseline)
    # 17:
    {'min_version': 13, 'flags': ""},                        # "CMOV"        supported by no flags
    {'min_version': 13, 'flags': ""},                        # "CX8"         supported by no flags
    {'min_version': 13, 'flags': ""},                        # "FPU"         supported by no flags
    {'min_version': 13, 'flags': "-mfxsr"},
    {'min_version': 13, 'flags': "-mmmx"},
    {'min_version': 13, 'flags': ""},                        # "SCE"         supported by no flags
    {'min_version': 13, 'flags': "-msse"},
    {'min_version': 13, 'flags': "-msse2"},

    # Level 2 - x86-64-v2
    {'min_version': 13, 'flags': "-mcx16"},
    {'min_version': 13, 'flags': "-msahf"},                 # Supported on Clang 6.0.1 but not supported on Clang 6.0.0, so the min Clang version is 7
    {'min_version': 13, 'flags': "-mpopcnt"},
    {'min_version': 13, 'flags': "-msse3"},
    {'min_version': 13, 'flags': "-msse4.1"},
    {'min_version': 13, 'flags': "-msse4.2"},
    {'min_version': 13, 'flags': "-mssse3"},

    # Level 3 - x86-64-v3
    {'min_version': 13, 'flags': "-mavx"},
    {'min_version': 13, 'flags': "-mavx2"},
    {'min_version': 13, 'flags': "-mbmi"},
    {'min_version': 13, 'flags': "-mbmi2"},
    {'min_version': 13, 'flags': "-mf16c"},
    {'min_version': 13, 'flags': "-mfma"},
    {'min_version': 13, 'flags': "-mlzcnt"},          # Clang does not have dual flag -mlzcnt -mabm, it just has -mlzcnt
    {'min_version': 13, 'flags': "-mmovbe"},
    {'min_version': 13, 'flags': "-mxsave"},

    # Level 4 - x86-64-v4
    {'min_version': 13, 'flags': "-mavx512f"},
    {'min_version': 13, 'flags': "-mavx512bw"},
    {'min_version': 13, 'flags': "-mavx512cd"},
    {'min_version': 13, 'flags': "-mavx512dq"},
    {'min_version': 13, 'flags': "-mavx512vl"},

    # Other Features ------------------------------------------

    {'min_version': 13, 'flags': "-msse4a"},
    {'min_version': 13, 'flags': "-mpku"},
    {'min_version': 13, 'flags': "-mpclmul"},
    {'min_version': 13, 'flags': "-mfsgsbase"},
    {'min_version': 13, 'flags': "-mrdrnd"},
    {'min_version': 13, 'flags': "-mfma4"},
    {'min_version': 13, 'flags': "-mxop"},
    {'min_version': 13, 'flags': "-mtbm"},
    {'min_version': 13, 'flags': "-mrdseed"},
    {'min_version': 13, 'flags': "-madx"},
    {'min_version': 13, 'flags': "-m3dnow"},
    {'min_version': 13, 'flags': "-m3dnowa"},                    # "3dnowext" enhanced 3DNow!
    {'min_version': 13, 'flags': "-mprfchw"},                    # "prefetchw"
    {'min_version': 13, 'flags': "-mprefetchwt1"},
    {'min_version': 13, 'flags': "-mclflushopt"},
    {'min_version': 13, 'flags': "-mxsaveopt"},
    {'min_version': 13, 'flags': "-mxsavec"},
    {'min_version': 13, 'flags': "-mxsaves"},
    {'min_version': 13, 'flags': "-mclwb"},
    {'min_version': 13, 'flags': "-mptwrite"},
    {'min_version': 13, 'flags': "-mrdpid"},
    {'min_version': 13, 'flags': "-msgx"},
    {'min_version': 13, 'flags': "-mgfni"},
    {'min_version': 13, 'flags': "-mvpclmulqdq"},
    {'min_version': 13, 'flags': "-mpconfig"},
    {'min_version': 13, 'flags': "-mwbnoinvd"},
    {'min_version': 13, 'flags': "-mmovdiri"},
    {'min_version': 13, 'flags': "-mmovdir64b"},
    {'min_version': 13, 'flags': "-mlwp"},
    {'min_version': 13, 'flags': "-mmwaitx"},
    {'min_version': 13, 'flags': "-mclzero"},
    None,                                                         # "invlpgb_tlbsync"         TODO(fernando): y este???? https://www.phoronix.com/news/AMD-Zen-3-Inst-Fixes-GCC11
    {'min_version': 13, 'flags': "-mshstk"},                      # "cet_ss"
    {'min_version': 13, 'flags': "-mavxvnni"},
    {'min_version': 13, 'flags': "-mrtm"},                        # "tsxrtm"
    None,                                                         # -mhle
    {'min_version': 13, 'flags': "-mwaitpkg"},
    {'min_version': 13, 'flags': "-menqcmd"},
    {'min_version': 13, 'flags': "-muintr"},
    {'min_version': 13, 'flags': "-mtsxldtrk"},
    {'min_version': 13, 'flags': "-mcldemote"},
    {'min_version': 13, 'flags': "-mserialize"},
    {'min_version': 13, 'flags': "-mhreset"},
    {'min_version': 13, 'flags': "-maes"},
    {'min_version': 13, 'flags': "-mvaes"},
    {'min_version': 13, 'flags': "-msha"},
    {'min_version': 13, 'flags': "-mkl"},
    {'min_version': 13, 'flags': "-mwidekl"},
    None,                                                         # -mavx512fp16
    {'min_version': 13, 'flags': "-mavx512pf"},
    {'min_version': 13, 'flags': "-mavx512er"},
    None,                                                         # -mavx5124vnniw
    None,                                                         # -mavx5124fmaps
    {'min_version': 13, 'flags': "-mavx512vbmi"},
    {'min_version': 13, 'flags': "-mavx512ifma"},
    {'min_version': 13, 'flags': "-mavx512vbmi2"},
    {'min_version': 13, 'flags': "-mavx512vpopcntdq"},
    {'min_version': 13, 'flags': "-mavx512bitalg"},
    {'min_version': 13, 'flags': "-mavx512vnni"},
    {'min_version': 13, 'flags': "-mavx512bf16"},
    {'min_version': 13, 'flags': "-mavx512vp2intersect"},
    {'min_version': 13, 'flags': "-mamx-bf16"},
    {'min_version': 13, 'flags': "-mamx-tile"},
    {'min_version': 13, 'flags': "-mamx-int8"},
    None,                      # "mmxext"
    None,                      # "xgetbv_ecx1"
    None,                      # "umip"
    None,                      # "sgx_lc"
    None,                      # "mcommit"
    None,                      # "rdpru"
    None,                      # "invpcid"
    None,                      # "sev_snp"
]


def get_available_extensions():
    data = []
    for f in extensions_map:
        data.append(int(f()))

    data += [0] * (KTH_EXTENSIONS_MAX - len(data))
    return data

def _to_chars_bin(data):
    res = []
    for x in data:
        res.append(str(x))
    return res

def _to_ints_bin(data):
    res = []
    for x in data:
        res.append(int(x))
    return res

# def _pad_right_array(data):
#     if len(data) >= len(extensions_map): return data
#     n = len(extensions_map) - len(data)
#     for i in range(n):
#         data.append(int(0))
#     return data

def encode_extensions(exts):
    exts = _to_chars_bin(exts)
    # print(exts)
    exts_str = ''.join(reversed(exts))
    # print(exts_str)
    exts_num = int(exts_str, 2)
    # print(exts_num)
    exts_num_b58 = base58_flex_encode(exts_num)
    return exts_num_b58

def decode_extensions(architecture_id):
    architecture_id = str(architecture_id)
    exts_num = base58_flex_decode(architecture_id)
    res = "{0:b}".format(exts_num)
    res = res.zfill(KTH_EXTENSIONS_MAX)
    return _to_ints_bin(list(reversed(res)))

# def get_architecture_id():
#     exts = get_available_extensions()
#     architecture_id = encode_extensions(exts)
#     return architecture_id

def extensions_to_names(exts):
    res = []
    for i in range(MIN_EXTENSION, len(exts)):
        if i >= len(extensions_names):
            continue

        if (exts[i] == 1):
            res.append(extensions_names[i])
    return res

# ----------------------------------------------------------------------

class Vendor(Enum):
    Other = 0,
    Intel = 1,
    AMD = 2,
    VIA = 3,
    Transmeta = 4,
    NSC = 5,
    KVM = 6,         # Kernel-based Virtual Machine
    MSVM = 7,        # Microsoft Hyper-V or Windows Virtual PC
    VMware = 8,
    XenHVM = 9,
    Bhyve = 10,
    Hygon = 11,


# Except from http://en.wikipedia.org/wiki/CPUID#EAX.3D0:_Get_vendor_ID
vendorMapping = {
	"AMDisbetter!": Vendor.AMD,
	"AuthenticAMD": Vendor.AMD,
	"CentaurHauls": Vendor.VIA,
	"GenuineIntel": Vendor.Intel,
	"TransmetaCPU": Vendor.Transmeta,
	"GenuineTMx86": Vendor.Transmeta,
	"Geode by NSC": Vendor.NSC,
	"VIA VIA VIA ": Vendor.VIA,
	"KVMKVMKVMKVM": Vendor.KVM,
	"Microsoft Hv": Vendor.MSVM,
	"VMwareVMware": Vendor.VMware,
	"XenVMMXenVMM": Vendor.XenHVM,
	"bhyve bhyve ": Vendor.Bhyve,
	"HygonGenuine": Vendor.Hygon,
}

def vendorID():
    v = cpuid.cpu_vendor()
    vend = vendorMapping.get(v, Vendor.Other)
    return vend

# def brandName():
#     if max_extended_function() >= 0x80000004:
#         return cpuid.cpu_name()
#     return "unknown"

# def cacheLine():
# 	if max_function_id() < 0x1:
# 		return 0

# 	_, ebx, _, _ = cpuid.cpuid(1)
# 	cache = (ebx & 0xff00) >> 5 # cflush size
# 	if cache == 0 and max_extended_function() >= 0x80000006:
# 		_, _, ecx, _ = cpuid.cpuid(0x80000006)
# 		cache = ecx & 0xff # cacheline size
# 	#TODO: Read from Cache and TLB Information
# 	return int(cache)

# def familyModel():
# 	if max_function_id() < 0x1:
# 		return 0, 0
# 	eax, _, _, _ = cpuid.cpuid(1)
# 	family = ((eax >> 8) & 0xf) + ((eax >> 20) & 0xff)
# 	model = ((eax >> 4) & 0xf) + ((eax >> 12) & 0xf0)
# 	return int(family), int(model)

# def threadsPerCore():
# 	mfi = max_function_id()
# 	if mfi < 0x4 or vendorID() != Vendor.Intel:
# 		return 1

# 	if mfi < 0xb:
# 		_, b, _, d = cpuid.cpuid(1)
# 		if (d & (1 << 28)) != 0:
# 			# v will contain logical core count
# 			v = (b >> 16) & 255
# 			if v > 1:
# 				a4, _, _, _ = cpuid.cpuid(4)
# 				# physical cores
# 				v2 = (a4 >> 26) + 1
# 				if v2 > 0:
# 					return int(v) / int(v2)
# 		return 1
# 	_, b, _, _ = cpuid.cpuid_count(0xb, 0)
# 	if b&0xffff == 0:
# 		return 1
# 	return int(b & 0xffff)


# def logicalCores():
#     mfi = max_function_id()
#     vend = vendorID()

#     if vend == Vendor.Intel:
#         # Use this on old Intel processors
#         if mfi < 0xb:
#             if mfi < 1:
#                 return 0
#             # CPUID.1:EBX[23:16] represents the maximum number of addressable IDs (initial APIC ID)
#             # that can be assigned to logical processors in a physical package.
#             # The value may not be the same as the number of logical processors that are present in the hardware of a physical package.
#             _, ebx, _, _ = cpuid.cpuid(1)
#             logical = (ebx >> 16) & 0xff
#             return int(logical)
#         _, b, _, _ = cpuid.cpuid_count(0xb, 1)
#         return int(b & 0xffff)
#     elif vend == Vendor.AMD or vend == Vendor.Hygon:
#         _, b, _, _ = cpuid.cpuid(1)
#         return int((b >> 16) & 0xff)
#     else:
#         return 0

# def physicalCores():
#     vend = vendorID()

#     if vend == Vendor.Intel:
#         return logicalCores() / threadsPerCore()
#     elif vend == Vendor.AMD or vend == Vendor.Hygon:
#         if max_extended_function() >= 0x80000008:
#             _, _, c, _ = cpuid.cpuid(0x80000008)
#             return int(c&0xff) + 1
#     return 0


# def support_rdtscp():
#     if max_extended_function() < 0x80000001: return False
#     _, _, _, d = cpuid.cpuid(0x80000001)
#     return (d & (1 << 27)) != 0


# ----------------------------------------------------------------------

def is_superset_of(a, b):
    n = min(len(a), len(b))

    for i in range(n):
        if a[i] < b[i]: return False

    for i in range(n, len(b)):
        if b[i] == 1: return False

    return True

def test_is_superset_of():
    assert(is_superset_of([], []))
    assert(is_superset_of([0], []))
    assert(is_superset_of([], [0]))
    assert(is_superset_of([0], [0]))
    assert(is_superset_of([0,0], [0,0]))
    assert(is_superset_of([0], [0,0]))
    assert(is_superset_of([0,0], [0]))
    assert(is_superset_of([1], [1]))
    assert(is_superset_of([1], [0]))
    assert(is_superset_of([1], []))

    assert(not is_superset_of([0], [1]))
    assert(not is_superset_of([], [1]))

# test_is_superset_of()

def set_diff(a, b):
    n = min(len(a), len(b))
    m = max(len(a), len(b))

    res = [0] * m

    for i in range(n):
        res[i] = a[i] - b[i]

    # for i in range(n, len(b)):
    #     if b[i] == 1: return False

    return res


# ----------------------------------------------------------------------

def filter_extensions(exts, os, comp, comp_ver):
    comp = adjust_compiler_name(os, comp)

    if comp not in extensions_flags:
        print(f"Compiler {comp} not supported.")
        return [0] * len(exts)

    flags = extensions_flags[comp]

    if flags is None:
        print(f"Compiler {comp} not supported.")
        return [0] * len(exts)

    res = []
    for i in range(MIN_EXTENSION):
        res.append(exts[i])

    for i in range(MIN_EXTENSION, len(exts)):
        if i >= len(flags):
            res.append(0)
            continue

        if flags[i] is None:
            res.append(0)
            continue

        # print(flags[i]['min_version'])
        # print(comp_ver)

        if flags[i]['min_version'] > comp_ver:
            res.append(0)
            continue

        res.append(exts[i])

    return res

def get_compiler_flags(exts, os, comp, comp_ver):
    comp = adjust_compiler_name(os, comp)
    # flags = extensions_flags[comp]
    if comp not in extensions_flags:
        print(f"Compiler {comp} not supported.")
        return [0] * len(exts)

    flags = extensions_flags[comp]

    if flags is None:
        print(f"Compiler {comp} not supported.")
        return [0] * len(exts)

    res = []
    for i in range(MIN_EXTENSION, len(flags)):
        flag_el = flags[i]
        if flag_el is None:
            continue
        flag = flag_el['flags']

        if isinstance(flag, list):
            if (exts[i] == 1):
                res.append(flag[1])
            else:
                res.append(flag[0])
        else:
            if (exts[i] == 1 and flag != ""):
                res.append(flag)

    # res = list(set(res))
    return " ".join(res)

def get_compiler_flags_arch_id(arch_id, os, comp, comp_ver):
    exts = decode_extensions(arch_id)
    return get_compiler_flags(exts, os, comp, comp_ver)



# -----------------------------------------------------------------


def all_exts_on():
    exts = list(map(lambda x : int(x) , KTH_MARCH_BUILD_VERSION_BITS))
    exts += [1] * (KTH_EXTENSIONS_MAX - len(exts))
    return exts

def all_exts_off():
    exts = list(map(lambda x : int(x) , KTH_MARCH_BUILD_VERSION_BITS))
    exts += [0] * (KTH_EXTENSIONS_MAX - len(exts))
    return exts

def level3_on():
    exts = list(map(lambda x : int(x) , KTH_MARCH_BUILD_VERSION_BITS))
    exts += [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    exts += [0] * (KTH_EXTENSIONS_MAX - len(exts))
    return exts

def get_all_data(os, comp, comp_ver):
    cpu_exts = get_available_extensions()
    cpu_marchid = encode_extensions(cpu_exts)
    cpu_names = extensions_to_names(cpu_exts)

    comp_exts = filter_extensions(cpu_exts, os, comp, comp_ver)
    comp_marchid = encode_extensions(comp_exts)
    comp_names = extensions_to_names(comp_exts)
    comp_flags = get_compiler_flags(comp_exts, os, comp, comp_ver)

    level3_exts = level3_on()
    level3_marchid = encode_extensions(level3_exts)
    level3_names = extensions_to_names(level3_exts)
    level3_flags = get_compiler_flags(level3_exts, os, comp, comp_ver)

    return {
        'cpu_exts': cpu_exts,
        'cpu_marchid': cpu_marchid,
        'cpu_names': cpu_names,

        'comp_exts': comp_exts,
        'comp_marchid': comp_marchid,
        'comp_names': comp_names,
        'comp_flags': comp_flags,

        'level3_exts': level3_exts,
        'level3_marchid': level3_marchid,
        'level3_names': level3_names,
        'level3_flags': level3_flags,
    }


def several_tests(os, comp, comp_ver):
    # print(get_all_data(os, comp, comp_ver))

    all_exts = all_exts_on()
    comp_exts = filter_extensions(all_exts, os, comp, comp_ver)
    flags = get_compiler_flags(comp_exts, os, comp, comp_ver)
    print(flags)

#     # exts = all_exts_off()
#     level3_exts = level3_on()
#     # print(level3_exts)

#     cpu_exts = get_available_extensions()
#     # print("full extensions array:     ", cpu_exts)
#     cpu_marchid = encode_extensions(cpu_exts)
#     print("your CPU march id: ", cpu_marchid)
#     cpu_names = extensions_to_names(cpu_exts)
#     print("your CPU extensions: ", cpu_names)


#     comp_exts = filter_extensions(cpu_exts, os, comp, comp_ver)
#     # print("filtered extensions array: ", filtered)

#     diff = set_diff(cpu_exts, comp_exts)
#     # print("Extensions not supported by your compiler: ", diff)
#     names = extensions_to_names(diff)
#     print("Extensions not supported by your compiler: ", names)


#     # print(is_superset_of(cpu_exts, comp_exts))
#     # print(is_superset_of(comp_exts, cpu_exts))

#     is_super_set = is_superset_of(comp_exts, level3_exts)
#     print("your compiler march is a superset of level3 exts: ", is_super_set)

#     comp_marchid = encode_extensions(comp_exts)
#     print("your compiler march id: ", comp_marchid)

#     names = extensions_to_names(comp_exts)
#     print("your compiler extensions: ", names)

#     comp_flags = get_compiler_flags(comp_exts, os, comp, comp_ver)
#     print("compiler flags for your extensions: ", comp_flags)

#     if is_super_set:
#         level3_marchid = encode_extensions(level3_exts)
#         print("Level3 march id: ", level3_marchid)

#         names = extensions_to_names(level3_exts)
#         print("Level3 extensions: ", names)

#         level3_flags = get_compiler_flags(level3_exts, os, comp, comp_ver)
#         print("Level3 compiler flags: ", level3_flags)


# def main():
#     # print(support_level1_features())
#     # print(support_level2_features())
#     # print(support_level3_features())
#     # print(support_level4_features())

#     # os = 'Linux'
#     # comp = 'gcc'
#     # comp_ver = 12

#     os = 'Macos'
#     comp = 'apple-clang'
#     comp_ver = 13

#     # os = 'Linux'
#     # comp = 'clang'
#     # comp_ver = 6

#     several_tests(os, comp, comp_ver)

#     # comp_flags2 = get_compiler_flags_arch_id(archid, os, comp, comp_ver)
#     # print(comp_flags2)

#     # for i in range(len(filtered)):
#     #     print(filtered[i])

# if __name__ == "__main__":
#     main()




# ---------------------------------------------------------------------------------------------------------------------------------------------
# Links


# https://github.com/klauspost/cpuid/blob/master/cpuid.go
# https://docs.microsoft.com/es-es/cpp/intrinsics/cpuid-cpuidex?view=msvc-170
# https://en.wikipedia.org/wiki/CPUID
# https://www.felixcloutier.com/x86/

# Intel
# https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-instruction-set-reference-manual-325383.pdf

# AMD64 Architecture Programmer’s Manual Volume 2: System Programming
#   https://www.amd.com/system/files/TechDocs/24593.pdf
# AMD64 Architecture Programmer’s Manual Volume 3: General-Purpose and System Instructions
#   https://www.amd.com/system/files/TechDocs/24594.pdf
# AMD CPUID Specification
#   https://www.amd.com/system/files/TechDocs/25481.pdf



# https://en.wikipedia.org/wiki/X86_Bit_manipulation_instruction_set#cite_note-fam16hsheet-4
# https://en.wikipedia.org/wiki/SSE4#POPCNT_and_LZCNT
# https://gcc.gnu.org/onlinedocs/gcc-12.1.0/gcc/x86-Options.html#x86-Options
# https://en.wikipedia.org/wiki/X86-64#Microarchitecture_levels
# https://gitlab.com/x86-psABIs/x86-64-ABI
# https://developers.redhat.com/blog/2021/01/05/building-red-hat-enterprise-linux-9-for-the-x86-64-v2-microarchitecture-level#background_of_the_x86_64_microarchitecture_levels
# https://lists.llvm.org/pipermail/llvm-dev/2020-July/143289.html

# https://gcc.gnu.org/onlinedocs/gcc-3.1.1/gcc/i386-and-x86-64-Options.html#i386%20and%20x86-64%20Options
# https://gcc.gnu.org/onlinedocs/gcc-3.2.3/gcc/i386-and-x86-64-Options.html#i386%20and%20x86-64%20Options
# https://gcc.gnu.org/onlinedocs/gcc-3.3.6/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options
# https://gcc.gnu.org/onlinedocs/gcc-3.4.6/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options

# https://gcc.gnu.org/onlinedocs/gcc-4.0.4/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.1.2/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.2.4/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.3.6/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.4.7/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.5.4/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.6.4/gcc/i386-and-x86_002d64-Options.html#i386-and-x86_002d64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.7.4/gcc/i386-and-x86-64-Options.html#i386-and-x86-64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.8.5/gcc/i386-and-x86-64-Options.html#i386-and-x86-64-Options
# https://gcc.gnu.org/onlinedocs/gcc-4.9.4/gcc/i386-and-x86-64-Options.html#i386-and-x86-64-Options

# https://gcc.gnu.org/onlinedocs/gcc-5.5.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-6.5.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-7.5.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-8.5.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-9.5.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-10.4.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-11.3.0/gcc/x86-Options.html#x86-Options
# https://gcc.gnu.org/onlinedocs/gcc-12.1.0/gcc/x86-Options.html#x86-Options

# ------------------------------------------------------------------------------------------------

# https://github.com/pixelb/scripts/blob/master/scripts/gcccpuopt

















# # -----------------------------------------------------------------

# def march_conan_manip(conanobj):
#     if conanobj.settings.arch != "x86_64":
#         return (None, None)

#     march_from = 'taken from cpuid'
#     march_id = get_architecture_id()

#     if conanobj.options.get_safe("march_id") is not None:
#         if conanobj.options.march_id == "_DUMMY_":
#             conanobj.options.march_id = march_id
#         else:
#             march_id = conanobj.options.march_id
#             march_from = 'user defined'
#             #TODO(fernando): check for march_id errors

#     conanobj.output.info("Detected microarchitecture ID (%s): %s" % (march_from, march_id))

#     return (march_id)

# def pass_march_to_compiler(conanobj, cmake):

#     if conanobj.options.get_safe("march_id") is not None:
#         march_id = str(conanobj.options.march_id)
#         flags = get_compiler_flags_arch_id(march_id,
#                                 str(conanobj.settings.os),
#                                 str(conanobj.settings.compiler),
#                                 float(str(conanobj.settings.compiler.version)))

#         conanobj.output.info("Compiler flags: %s" % flags)
#         conanobj.output.info("Prev CONAN_CXX_FLAGS: %s" % cmake.definitions.get("CONAN_CXX_FLAGS", ""))
#         conanobj.output.info("Prev CONAN_C_FLAGS: %s" % cmake.definitions.get("CONAN_C_FLAGS", ""))

#         cmake.definitions["CONAN_CXX_FLAGS"] = cmake.definitions.get("CONAN_CXX_FLAGS", "") + " " + flags
#         cmake.definitions["CONAN_C_FLAGS"] = cmake.definitions.get("CONAN_C_FLAGS", "") + " " + flags

#     # if conanobj.settings.compiler != "Visual Studio":
#     #     gcc_march = str(conanobj.options.microarchitecture)
#     #     cmake.definitions["CONAN_CXX_FLAGS"] = cmake.definitions.get("CONAN_CXX_FLAGS", "") + " -march=" + gcc_march
#     #     cmake.definitions["CONAN_C_FLAGS"] = cmake.definitions.get("CONAN_C_FLAGS", "") + " -march=" + gcc_march
#     # else:
#     #     ext = msvc_to_ext(str(conanobj.options.microarchitecture))

#     #     if ext is not None:
#     #         cmake.definitions["CONAN_CXX_FLAGS"] = cmake.definitions.get("CONAN_CXX_FLAGS", "") + " /arch:" + ext
#     #         cmake.definitions["CONAN_C_FLAGS"] = cmake.definitions.get("CONAN_C_FLAGS", "") + " /arch:" + ext




# # -----------------------------------------------------------------



# #TODO(fernando): implementar RTCounter() del proyecto Golang
# #TODO(fernando): implementar Ia32TscAux() del proyecto Golang

# # LogicalCPU will return the Logical CPU the code is currently executing on.
# # This is likely to change when the OS re-schedules the running thread
# # to another CPU.
# # If the current core cannot be detected, -1 will be returned.
# def LogicalCPU():
#     if max_function_id() < 1:
#         return -1
#     _, ebx, _, _ = cpuid.cpuid(1)
#     return int(ebx >> 24)


# # VM Will return true if the cpu id indicates we are in
# # a virtual machine. This is only a hint, and will very likely
# # have many false negatives.
# def VM():
#     vend = vendorID()
#     if vend == Vendor.MSVM or vend == Vendor.KVM or vend == Vendor.VMware or vend == Vendor.XenHVM or vend == Vendor.Bhyve:
#         return True
#     return False

# def Hyperthreading():
#     if max_function_id() < 4: return False
#     _, _, _, d = cpuid.cpuid(1)
#     if vendorID() == Vendor.Intel and (d&(1<<28)) != 0:
#         if threadsPerCore() > 1:
#             return True
#     return False


# # -----------------------------------------------------------------
# # OS support
# # -----------------------------------------------------------------

# # XSAVE family
# def support_osxsave():
#     if max_function_id() < 0x00000001: return False
#     _, _, c, _ = cpuid.cpuid(0x00000001)
#     return (c & (1 << 27)) != 0

# # OSPKE (Instructions RDPKRU, WRPKRU)
# # OS has enabled Memory Protection Keys and use of the RDPKRU/WRPKRU instructions by setting CR4.PKE=1.
# # Note(fernando): I think it is related to PKU
# # 0000_0007_0 ECX[4]
# # Note(fernando): We do not need to check OS flags. We just need to check CPU flags because
# def support_ospke_unused():
#     # if max_function_id() < 0x00000007: return False
#     # _, _, c, _ = cpuid.cpuid_count(0x00000007, 0)
#     # return (c & (1 << 4)) != 0
#     return False

# # https://en.wikipedia.org/wiki/Advanced_Vector_Extensions#Operating_system_support
# def support_avx_os():
#     # Copied from: http://stackoverflow.com/a/22521619/922184

#     if max_function_id() < 0x00000001: return False
#     _, _, c, _ = cpuid.cpuid(0x00000001)

#     XGETBV = (c & (1 << 26)) != 0
#     osUsesXSAVE_XRSTORE = (c & (1 << 27)) != 0
#     cpuAVXSuport = (c & (1 << 28)) != 0

#     if not (XGETBV and osUsesXSAVE_XRSTORE and cpuAVXSuport):
#         return False

#     xcrFeatureMask = cpuid.xgetbv(0)
#     return (xcrFeatureMask & 0x6) == 0x6

# def support_avx2_os():
#     return support_avx_os() and support_avx2_cpu()

# def support_fma3_os():
#     return support_avx_os() and support_fma3_cpu()

# def support_fma4_os():
#     return support_avx_os() and support_fma4_cpu()

# def support_xsave_os():
#     return support_xsave_cpu() and support_osxsave()

# def support_xsaveopt_os():
#     return support_xsaveopt_cpu() and support_xsave_os()

# def support_xsavec_os():
#     return support_xsavec_cpu() and support_xsave_os()

# def support_xsaves_os():
#     return support_xsaves_cpu() and support_xsave_os()

# def support_avx512_os():
#     if max_function_id() < 0x00000001: return False
#     _, _, c, _ = cpuid.cpuid(0x00000001)

#     # Only detect AVX-512 features if XGETBV is supported
#     if c & ((1<<26)|(1<<27)) != (1<<26)|(1<<27): return False

#     # Check for OS support
#     eax = cpuid.xgetbv(0)

#     # Verify that XCR0[7:5] = 111b (OPMASK state, upper 256-bit of ZMM0-ZMM15 and
#     # ZMM16-ZMM31 state are enabled by OS)
#     #  and that XCR0[2:1] = 11b (XMM state and YMM state are enabled by OS).
#     return (eax>>5)&7 == 7 and (eax>>1)&3 == 3

# def support_avx512f_os():
#     return support_avx512_os() and support_avx512f_cpu()

# def support_avx512pf_os():
#     return support_avx512_os() and support_avx512pf_cpu()

# def support_avx512er_os():
#     return support_avx512_os() and support_avx512er_cpu()

# def support_avx512vl_os():
#     return support_avx512_os() and support_avx512vl_cpu()

# def support_avx512bw_os():
#     return support_avx512_os() and support_avx512bw_cpu()

# def support_avx512dq_os():
#     return support_avx512_os() and support_avx512dq_cpu()

# def support_avx512cd_os():
#     return support_avx512_os() and support_avx512cd_cpu()

# def support_avx5124vnniw_os():
#     return support_avx512_os() and support_avx5124vnniw_cpu()

# def support_avx5124fmaps_os():
#     return support_avx512_os() and support_avx5124fmaps_cpu()

# def support_avx512vbmi_os():
#     return support_avx512_os() and support_avx512vbmi_cpu()

# def support_avx512ifma_os():
#     return support_avx512_os() and support_avx512ifma_cpu()

# def support_avx512vbmi2_os():
#     return support_avx512_os() and support_avx512vbmi2_cpu()

# def support_avx512vpopcntdq_os():
#     return support_avx512_os() and support_avx512vpopcntdq_cpu()

# def support_avx512bitalg_os():
#     return support_avx512_os() and support_avx512bitalg_cpu()

# def support_avx512vnni_os():
#     return support_avx512_os() and support_avx512vnni_cpu()

# def support_avx512bf16_os():
#     return support_avx512_os() and support_avx512bf16_cpu()

# def support_avx512vp2intersect_os():
#     return support_avx512_os() and support_avx512vp2intersect_cpu()

# # ------------------------------------------------------------------------------------------
