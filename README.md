# EEG-
EEG hardware project. Device based on STM32

**Hardware**
 - STM32F446RE
 - BLE module
 - USB Isolator
 - AFE
 - 

**Software & Tools**
  - STM32CubeIDE

**Electrodes**

**Reference Open source projects**
  - STM32 shield for EEG/EMG/ECG https://pieeg.com/microbci/
    8 channels, NUCLEO-WB55 compatible, Python software
  - https://github.com/pieeg-club/ironbci
  - https://www.crowdsupply.com/neuroidss/freeeeg32
  - https://www.hackster.io/mustafamelihcan/open-source-diy-eeg-brainwaves-on-a-custom-pcb-99146e

┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Electrodes │───▶│  AFE         │───▶│  STM32 MCU  │───▶│  Output      │
│  (Scalp)    │    │  (ADS1299)   │    │  (F4/H7)    │    │  (USB/BLE)   │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                         │                    │
                   ┌─────┴─────┐        ┌─────┴─────┐
                   │ SPI Bus   │        │ DSP/Filter│
                   │ (16 MHz)  │        │ Processing│
                   └───────────┘        └───────────┘
