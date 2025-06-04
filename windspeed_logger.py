import spidev
import time
import csv

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 1)  # Use (0, 1) if you're using CE1 (GPIO 7)
spi.max_speed_hz = 1350000

def read_adc(channel):
    if not 0 <= channel <= 7:
        raise ValueError("ADC channel must be 0-7")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def adc_to_voltage(adc_value):
    return (adc_value * 3.3) / 1023

def voltage_to_windspeed(voltage):
    # Adjust this formula based on your sensor's datasheet (Adafruit 1733)
    return max(0.0, (voltage - 0.4) * 20.25)

def log_to_csv(windspeed):
    with open("windspeed_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([time.strftime("%d-%m-%Y %H:%M"), windspeed])

try:
    while True:
        adc_val = read_adc(0)  # Reading from CH0
        voltage = adc_to_voltage(adc_val)
        windspeed = voltage_to_windspeed(voltage)
        print(f"Voltage: {voltage:.2f} V | Wind Speed: {windspeed:.2f} m/s")
        log_to_csv(windspeed)
        time.sleep(300)  # every 5 minutes

except KeyboardInterrupt:
    print("\nStopped.")
finally:
    spi.close()

