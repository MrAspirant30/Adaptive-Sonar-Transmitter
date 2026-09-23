#include <Arduino.h>
#include "waveform_buffer.h"

#define DAC_PIN 25

volatile uint16_t sample_index = 0;

hw_timer_t *timer = NULL;

void ARDUINO_ISR_ATTR onTimer()
{
    dacWrite(DAC_PIN, waveform_buffer[sample_index]);

    sample_index++;

    if (sample_index >= WAVEFORM_SIZE)
    {
        sample_index = 0;
    }
}

void setup()
{
    Serial.begin(115200);

    delay(1000);

    Serial.println("===================================");
    Serial.println("      ESP32 LFM DAC OUTPUT TEST");
    Serial.println("===================================");

    Serial.print("Waveform samples : ");
    Serial.println(WAVEFORM_SIZE);

    Serial.print("Sample rate      : ");
    Serial.println(100000);

    Serial.println("DAC output pin   : GPIO25");

    // Timer clock = 80 MHz / 80 = 1 MHz
    timer = timerBegin(0, 80, true);

    // Attach interrupt
    timerAttachInterrupt(timer, &onTimer, true);

    // Trigger every 10 timer ticks = 10 microseconds
    timerAlarmWrite(timer, 10, true);

    // Enable timer alarm
    timerAlarmEnable(timer);

    Serial.println("Timer configured.");
    Serial.println("Ready for LFM output.");
}

void loop()
{
}