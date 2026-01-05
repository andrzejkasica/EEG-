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
  - https://pieeg.com/microbci/
    STM32 shield for EEG/EMG/ECG,
    8 channels, NUCLEO-WB55 compatible, Python software
  - https://github.com/pieeg-club/ironbci
    Wearable BCI with ADS1299 + STM32 
    BLE, mobile SDK, 3D printable headset designs
  - https://www.crowdsupply.com/neuroidss/freeeeg32
    32-channel research-grade EEG
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
