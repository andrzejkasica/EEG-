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
  - Wearable BCI with ADS1299 + STM32 https://github.com/pieeg-club/ironbci
    BLE, mobile SDK, 3D printable headset designs
  - 32-channel research-grade EEG https://www.crowdsupply.com/neuroidss/freeeeg32
    STM32H7, 4x AD7771 ADCs, high-quality acquisition
  - https://www.hackster.io/mustafamelihcan/open-source-diy-eeg-brainwaves-on-a-custom-pcb-99146e
    Single-channel custom PCB EEG

**Diagram**
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Electrodes │───▶│  AFE         │───▶│  STM32 MCU  │───▶│  Output      │
│  (Scalp)    │    │  (ADS1299)   │    │  (F4/H7)    │    │  (USB/BLE)   │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                         │                    │
                   ┌─────┴─────┐        ┌─────┴─────┐
                   │ SPI Bus   │        │ DSP/Filter│
                   │ (16 MHz)  │        │ Processing│
                   └───────────┘        └───────────┘
