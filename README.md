What this is: 

Draw a pattern for your signal, get an array of RGB values to put into your LED control algorithm.

TODO: Add a demo GIF here.

Example:

So let's say you want to create a pattern for an RGB LED which repeats every second. Pattern is a an initial spike of purple light followd by several spikes of lower intensity.

Let's stop at the resolution of 8 bits - this means that to get the maximum accuracy out of your LED control system, you'd need to use an image with height of 256px.

Each pixel represents a single time step. So if your LED update algorithm runs at 1kHz, period between time steps is 1ms and to create a pattern lasting 1s you'd need to create an image of width = 1000px.

Once you've draw your pattern, just feed it to the python script like so:

	python img_to_array.py pattern.png

On the output you'll get get an array of values in the following form:

	#define PATTERN_LENGTH ...
	const uint8_t pattern[] = { ... };

Then in your LED update function you'd do something like this:

	void LED_Update(void)
	{
		if (index <= (PATTERN_LENGTH - 2) && (index > 0))
			index += 3;
		else
			index = 0;

		uint8_t r_value = pattern[index    ];
		uint8_t g_value = pattern[index + 1];
		uint8_t b_value = pattern[index + 2];
		
		LED_SetColor(r_value, g_value, b_value);
	}
