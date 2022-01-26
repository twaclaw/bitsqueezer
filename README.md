# Bit Squeezer

*bitsqueezer* provides a reference implementation illustrating how to perform basic bit-compression. This compression is useful when transmitting data across channels with restricted bandwidth (e.g., when using protocols like [LoRaWAN](https://lora-developers.semtech.com/documentation/tech-papers-and-guides/lora-and-lorawan)). 

The Python code is written in a  way that it can be easily translated to other languages. The compression part, for instance,  can be translated to C.

The following points exemplify the type of compression that *bitsqueezer* performs:

* Let's assume we want to transmit a given set of variables; for instance, a pair of temperature and humidity values: $17.3$ C and $53$%.
* In microcontroller applications, these values are usually encoded as integers, for instance: $1730$ (with two decimal places) and $53$ (no decimal places), respectively.
* Instead of defining standard types for these values (e.g. `int16` and `uint8`), we can find the exact number of bits required for each variable, for instance,  based on the resolution and the range of a sensor. In the example above, the temperature reading has two decimal places, if we assume that the range of the sensor is $[-80, 80]$ C, encoded as $[-8000, 8000]$, then we would need $\log_{2}(16000)\approx 14$ bits.
* By using only the strictly required number of bits instead of the integer types provided by the architecture, we can gain some bits. The cumulated effect of this bit economy results in better utilization of the channel.
* To continue with the example, the temperature and humidity values can be represented by $14$ and $7$ bits, respectively. $14 + 7 = 21$ doesn't seem like a huge improvement compared to $16 + 8 = 24$ (if we were to use the standard types `int16` and `uint8`, respectively); however, it is the cumulative effect what matters. For instance, if we are transmitting a buffer containing 50 pairs of temperature and humidity values, we would require $(14 + 7)*100/8 = 131$ instead of $(16 + 8)/8 = 150 $ bytes.

## Example

The following example requires `Numpy`.

```bash
python main.py 
Ready to compress vars: [-1730, 65, 355, 1425]
Compressed buffer: byte-ptr:6, bit-ptr: 3, buff:858de05880c802
Ready to compress vars: [-865, 32, 177, 712]
Compressed buffer: byte-ptr:12, bit-ptr: 6, buff:858de05880c81a36806201200b
Decompressed vars: [[-1730, 65, 355, 1425], [-865, 32, 177, 712]]

```