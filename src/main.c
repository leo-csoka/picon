#include "pico/stdlib.h"
#include "btstack.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "joycon.h"
#include "joycon_bt.h"

// constants
#define BUFFER_SIZE 128
#define MAX_TOKENS 9
#define BUTTON_COUNT ((int)(sizeof(buttons) / sizeof(buttons[0])))
static const char *buttons[] = {"DUP", "DDOWN", "DLEFT", "DRIGHT", "SR", "SL", "MINUS"};

static Joycon *jc;
static btstack_timer_source_t serial_timer;



static void serial_tick(btstack_timer_source_t *timer) {
    static char buffer[BUFFER_SIZE];
    static int buffer_index = 0;

    while (true) {
        int c = getchar_timeout_us(0);
        if (c == PICO_ERROR_TIMEOUT) break;

        // per buffer line
        if (c == '\n' || c == '\r') {
            // mark end of line in buffer
            buffer[buffer_index] = '\0';

            // tokenize the buffer for each comma separated input
            char *token = strtok(buffer, ",");
            char *values[MAX_TOKENS];
            int count = 0;

            while (token != NULL && count < MAX_TOKENS) {
                values[count++] = token;
                token = strtok(NULL, ",");
            }

            // skip empty/partial lines (e.g. the second half of a \r\n)
            if (count >= 2 && jc->get_pair_state(jc) == JOYCON_CONNECTED) {
                
                /* update stick positions */
                float sticks[4] = {(float)atof(values[0]), (float)atof(values[1]), 0.0f, 0.0f};
                jc->stick_update(jc, sticks);

                /* update button states (tokens 3 to 9) */
                for (int i = 0; i < count - 2 && i < BUTTON_COUNT; i++) {
                    if (atoi(values[i + 2])) {
                        jc->press(jc, buttons[i]);
                    } else {
                        jc->release(jc, buttons[i]);
                    }
                }
            }

            buffer_index = 0;
        } else if (buffer_index < BUFFER_SIZE - 1) {
            // add character to string buffer
            buffer[buffer_index++] = (char)c;
        }
    }

    btstack_run_loop_set_timer(timer, 20);
    btstack_run_loop_add_timer(timer);
}


int main(void) {
    /* build and initialize controller */
    stdio_init_all();

    jc = joycon_create(JOYCON_LEFT, JC_COLOR_NEON_ORANGE);
    joycon_bt_init(jc);

    btstack_run_loop_set_timer_handler(&serial_timer, serial_tick);
    btstack_run_loop_set_timer(&serial_timer, 20);
    btstack_run_loop_add_timer(&serial_timer);

    joycon_bt_run();
    return 0;
}
