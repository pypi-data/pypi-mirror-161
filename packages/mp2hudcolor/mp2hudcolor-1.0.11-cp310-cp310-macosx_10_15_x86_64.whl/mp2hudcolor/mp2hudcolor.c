#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static const uint32_t TWGC_ID = 0x7FDA1466;
static const uint16_t TWGC_DATA_SIZE = 6097 + 50;
static const uint32_t TWGC_IDS[] = {
    0xC8DDC662, 0x79EA6F12, 0xABE766B0, 0x43ED3310, 0xC4E17CA8, 0x5BA76807, 0x29453102, 0xCDBD73E1, 0xE846D37F, 0x3BFFE826, 0x7D2500D2, 0xA947A67C, 0x2D5344F, 0xACF62D93, 0xC7182898, 0x507B51DA, 0xD3BAFAF5, 0xEA4347BC, 0x8B7D7378, 0xBA6C75A2, 0x13490420, 0xF7283644, 0x4E77411, 0x716E6398, 0x4D916BB8, 0x4CB38E71, 0x37E381C2, 0x3C5D7111, 0xC758541F, 0x87D3CE8A, 0xC01F5F88, 0xB6A61E34, 0xF8B971FA, 0x4280D00A, 0xAFE2D45D, 0x83040135, 0x13BD3B64, 0x88936AA2, 0x142CB7A1, 0x439A3774, 0xC54FA7BC, 0x5FF96AF1, 0x37564B7D, 0x5368A35F, 0x6F6E9D6D, 0xBB0897EA, 0x2DF1EB03, 0x95CC4ED8, 0x27D0C234, 0x63384F81, 0xF37E756, 0x659147AE, 0xF9E7E0DF, 0x92B8C50F, 0x59148173, 0xF895098F, 0xE0290C48, 0xF4379CF4, 0xCE7C9D8D, 0xC3C55C9, 0x823E2FB3, 0xC37D11B7, 0xDF706404, 0x8B0A4C90, 0xE4C1BBEB, 0x1A8B61B8, 0x6991E2CD, 0x70A2CD6E, 0xAE1317D8, 0x6BF04FF9, 0x5A807B81, 0xB9A9FC6E, 0xA8698FE8, 0x74E5FFA1, 0x867B01A2, 0x89A45BCB, 0xDAA7D80, 0xE8401C5A, 0x5BF10430, 0x150A9B17, 0x2F3CACAF, 0x26E1EB8C, 0x1531EDD3, 0xDEFCA700, 0x74353DC4, 0xF8170D6, 0x14558146, 0xE1FF2A4F, 0x1EC7F863, 0x92F59138, 0xEC4197E3, 0x3AEE673F, 0x9B27BE10, 0xBDB697A9, 0x59E416AA, 0xCEB17CDF, 0x8BE8347, 0x35402188, 0x448156AE, 0xA09CAEFE, 0x2EAFEDF7, 0x4F1D443E, 0xA485372C, 0x421BAE2A, 0xA709DB40, 0x42E2DFC1, 0x4A7A4D45, 0xDB2CA6FF, 0x18717FA7, 0xB0253266, 0xD66D715F, 0xDCAAB836, 0xC87C1FF5, 0x844AB6B0, 0x794204FD, 0xA59B3320, 0x149369FD, 0xAA4A5604, 0xB5DA30F4, 0xCEC78E81, 0x76357179, 0x2A01734F, 0x166C22E0, 0xC12CBAB9, 0x22B9B01E, 0x81269EE0, 0xDDC561EB, 0xC18BDC67, 0x4B86C539, 0x738D9C43, 0x78522461, 0x19E9738B, 0xD24AE6B, 0x64337CCD, 0x6A839A97, 0xF36ADACB, 0xF17911AA, 0x34F26028, 0x5A6587DF, 0xD110A12F, 0xA6609CC5, 0xBAA6D6A1, 0x3C1AE0FF, 0xCA7BEB2, 0xC61D97EF, 0x1ADEA12B, 0xCBB3FB76, 0xF37F8DEB, 0x6C8550C9, 0x2AF5AA06, 0x9BE28150, 0xA781ED1D, 0x74BB42F, 0x9329C6FF, 0x5E5B8C0A, 0xC2A8CCC6, 0x8ED04C36, 0xE6EC3C8D, 0x66B7EDA3, 0x4C5AFF4F, 0x779C7B9C, 0x591CD695, 0xEB7EB756, 0x8EE94C81, 0x223058B5, 0xDE649E48, 0x7B2EC4E, 0x91338F72, 0x3D27FFD, 0x345E5B4E, 0xC1EC3637, 0xEB63AFED, 0xDACA46D4, 0xA14C8D20, 0x63E9E374, 0xAAF6E9A9, 0x1A96EC67, 0xB17B693, 0x23CAC744, 0xEF1EC40E, 0x1B0F3A85, 0xCCEE3FEB, 0x5C336F85, 0xB4135CDD, 0x51C5AAD9, 0x6CCCDF8F, 0xFAD063D5, 0xCB7DDAF4, 0x96F650C3, 0x949B0FFF, 0xCA68F68F, 0xF0C61AF5, 0x4377E677, 0xDC901206, 0xC00A29F, 0xF0049167, 0x60E8322B, 0xABDBFA5B, 0xD3CBE846, 0xA42F6495, 0xF6451DA, 0xF9C88B05, 0x1FD3D43A, 0x9CFB8A36, 0xBE3C29A1, 0xFDCD9589, 0x8C9F2A1A, 0x9DA5D1D7, 0xBFFFE95A, 0xAF0001CF, 0xE7070332, 0x4C215775
};
#define NTWK_MAX_FILE_SIZE (0x8000)

static void _usage(void)
{
    printf("Rewrites TweakGuiColors (TWGC) in the provided Metroid Prime 2: Echoes NTWK file to use a custom color. Color format is RGB as floats between 0.0-1.0.\n");
    printf("Usage:\n");
    printf("\tmp2hudcolor <inputFile> <outputFile> <red> <green> <blue>\n");
}

static float _swap_endianess_float(uint8_t* data)
{
    uint8_t four[4];
    four[0] = data[3];
    four[1] = data[2];
    four[2] = data[1];
    four[3] = data[0];
    return *((float*)four);
}

static uint32_t _swap_endianess_u32(uint8_t* data)
{
    uint8_t four[4];
    four[0] = data[3];
    four[1] = data[2];
    four[2] = data[1];
    four[3] = data[0];
    return *((uint32_t*)four);
}

static uint16_t _swap_endianess_u16(uint8_t* data)
{
    uint8_t two[2];
    two[0] = data[1];
    two[1] = data[0];
    return *((uint16_t*)two);
}

void mp2hudcolor(char* input_filename, char* output_filename, float r, float g, float b)
{
    static uint8_t buff[NTWK_MAX_FILE_SIZE];

    // Check input
    if (
        r > 1.00001 || r < -0.00001
        || g > 1.00001 || g < -0.00001
        || b > 1.00001 || b < -0.00001
    )
    {
        printf("Error - Input color must be 0.0 - 1.0\n");
        return;
    }

    float rgb_max = r > g ? r : g;
    rgb_max = b > rgb_max ? b : rgb_max;

    // Open input file
    long ntwk_size = 0;
    {
        FILE *src = fopen(input_filename, "rb");
        if (src == NULL)
        {
            printf("Error - Failed to open '%s' for reading\n", input_filename);
            return;
        }

        // Check file size
        fseek(src, 0L, SEEK_END);
        ntwk_size = ftell(src);
        rewind(src);
        if (ntwk_size > NTWK_MAX_FILE_SIZE)
        {
            printf("Error - Unexpected input file size - %ld\n", ntwk_size);
            return;
        }

        // Read file to RAM
        size_t result = fread(buff, ntwk_size, 1, src);
        fclose(src);
        if (result != 1)
        {
            printf("Error - Failed to read input file\n");
            return;
        }
    }

    // Find the start of TWGC
    unsigned twgc_start = 0;
    for (unsigned i = 0; i < ntwk_size-4; i++)
    {
        if ((buff[i] != 'T') || (buff[i + 1] != 'W') || (buff[i + 2] != 'G') || (buff[i + 3] != 'C'))
        {
            continue;
        }
        twgc_start = i;
        break;
    }

    if (!twgc_start)
    {
        printf("Error - Failed to find start of TWGC\n");
        return;
    }

    // Modify file in RAM
    for (unsigned i = 0; i < sizeof(TWGC_IDS) / 4; i++)
    {
        unsigned found = 0;
        for (unsigned j = 0; j < TWGC_DATA_SIZE; j++)
        {
            // Check for ID
            uint8_t* data = buff + twgc_start + j;
            if (_swap_endianess_u32(data) != TWGC_IDS[i])
            {
                continue;
            }

            // if (found)
            // {
            //     printf("Warning - Found second instance of tweak ID 0x%X\n", TWGC_IDS[i]);
            // }

            found = 1;

            data = data + 4; // advance length of uint32_t size
            uint16_t size = _swap_endianess_u16(data);
            if (size != 0x10)
            {
                // printf("Warning - Unexpected RGBA size %d (tweak ID 0x%X)\n", size, TWGC_IDS[i]);
                continue;
            }

            data = data + 2; // advance length of uint16_t size
            float old_r = _swap_endianess_float(data);
            float old_g = _swap_endianess_float(data + 4);
            float old_b = _swap_endianess_float(data + 8);
            float old_a = _swap_endianess_float(data + 12);

            // Check for non-color
            if (
                old_r > 1.00001 || old_r < -0.00001
                || old_g > 1.00001 || old_g < -0.00001
                || old_b > 1.00001 || old_b < -0.00001
                || old_a > 1.00001 || old_a < -0.00001
            )
            {
                printf("Warning - Unexpected rgba value (%f, %f, %f, %f)\n", old_r, old_g, old_b, old_a);
                continue;
            }

            // Skip black/white/gray
            if (
                old_r-old_g > -0.1 && old_r-old_g < 0.1
                && old_r-old_b > -0.1 && old_r-old_b < 0.1
                && old_g-old_b > -0.1 && old_g-old_b < 0.1
            )
            {
                continue;
            }

            // Scale color to match vibrance of original
            float rgb_old_max = old_r > old_g ? old_r : old_g;
            rgb_old_max = old_b > rgb_old_max ? old_b : rgb_old_max;
            float scale = rgb_old_max / rgb_max;

            float new_r = r*scale;
            float new_g = g*scale;
            float new_b = b*scale;

            // printf("0x%X - %f, %f, %f\n", (unsigned) (data - buff), old_r, old_g, old_b);
            float* data_f = (float*)data;
            data_f[0] = _swap_endianess_float((void*)&new_r);
            data_f[1] = _swap_endianess_float((void*)&new_g);
            data_f[2] = _swap_endianess_float((void*)&new_b);
        }

        if (!found)
        {
            printf("Warning - Failed to find and replace color 0x%X\n", TWGC_IDS[i]);
        }
    }

    // Write back
    FILE *dst = fopen(output_filename, "wb");
    if (dst == NULL)
    {
        printf("Error - Failed to open '%s' for writing\n", output_filename);
        return;
    }
    fseek(dst, 0, SEEK_SET);
    fwrite(buff, ntwk_size, 1, dst);
    fclose(dst);
}

int main(int argc, char *argv[])
{
    // Parse input
    if (argc != 6)
    {
        _usage();
        return -1;
    }

    float r = atof(argv[3]);
    if (r < -0.00001 || r > 1.00001)
    {
        _usage();
        return -1;
    }

    float g = atof(argv[4]);
    if (g < -0.00001 || g > 1.00001)
    {
        _usage();
        return -1;
    }

    float b = atof(argv[5]);
    if (b < -0.00001 || b > 1.00001)
    {
        _usage();
        return -1;
    }

    mp2hudcolor(argv[1], argv[2], r, g, b);
    return 0;
}
