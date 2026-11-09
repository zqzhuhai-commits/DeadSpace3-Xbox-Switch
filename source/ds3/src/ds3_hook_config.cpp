// Shared settings for the base and Awakened hooks.
#include <cstdint>
#include <rex/cvar.h>

REXCVAR_DEFINE_INT32(ds3_prioridad_mezclador, 0x2E, "DS3",
                     "Prioridad de Horizon de los hilos de mezcla de audio del juego (0x2C-0x3A); 0 = la de los "
                     "demas hilos del juego (0x3B)")
    .range(0, 0x3B);

REXCVAR_DEFINE_BOOL(ds3_audio_sin_compresor, true, "DS3",
                    "Saltarse el compresor final del audio del juego (su propio camino de bypass): parte del hilo de "
                    "mezcla. false = el sonido original, mas CPU");

REXCVAR_DEFINE_BOOL(ds3_audio_nativo, true, "DS3",
                    "MixWithGain y CopyWithGain del mezclador en NEON nativo en vez de traducidos");

REXCVAR_DEFINE_INT32(ds3_espera_gpu_us, 100, "DS3",
                     "Microsegundos que duerme la espera activa de Direct3D a la GPU (0x88A20950) tras las cesiones; "
                     "0 = girar como en la Xbox 360")
    .range(0, 2000);

REXCVAR_DEFINE_INT32(ds3_espera_gpu_cesiones, 32, "DS3",
                     "Veces que la espera de Direct3D a la GPU solo cede el nucleo antes de dormir")
    .range(0, 100000);
