

/*
 * Determine if a keypress would modify the value of a textbox.
 *
 * Note that this implies that the keypress is also *valid* in the context of a
 * numeric textbox.
 *
 * Returns `true` if the keypress is valid and would modify the textbox value,
 * or `false` otherwise.
 */
function key_modifies(event) {

    if (event.which >= 48 && event.which <= 57) {       // Numeric (QWERTY)
        if (! event.shiftKey) {  // shift key means punctuation instead of numeric
            return true;
        }

    } else if (event.which >= 96 && event.which <= 105) { // Numeric (10-Key)
        return true;

    } else if (event.which == 109 || event.which == 173) { // hyphen (negative sign)
        return true;

    } else if (event.which == 110 || event.which == 190) { // period/decimal
        return true;

    } else if (event.which == 8) {                      // Backspace
        return true;

    } else if (event.which == 46) {                     // Delete
        return true;
    } else if (event.ctrlKey && event.which == 86) {    // Ctrl+V
        return true;
    } else if (event.ctrlKey && event.which == 88) {    // Ctrl+X
        return true;
    }

    return false;
}


/*
 * Determine if a keypress is allowed in the context of a textbox.
 *
 * The purpose of this function is to let certain "special" keys (e.g. function
 * and navigational keys) to pass through, so they may be processed as they
 * would for a normal textbox.
 *
 * Note that this function does *not* check for keys which would actually
 * modify the value of the textbox.  It is assumed that the caller will have
 * already used `key_modifies()` for that.
 *
 * Returns `true` if the keypress is allowed, or `false` otherwise.
 */
function key_allowed(event) {

    // Allow anything with modifiers (except Shift).
    if (event.altKey || event.ctrlKey || event.metaKey) {

        // ...but don't allow Ctrl+X or Ctrl+V
        return event.which != 86 && event.which != 88;
    }

    // Allow function keys.
    if (event.which >= 112 && event.which <= 123) {
        return true;
    }

    // Allow Home/End/arrow keys.
    if (event.which >= 35 && event.which <= 40) {
        return true;
    }

    // Allow Tab key.
    if (event.which == 9) {
        return true;
    }

    // allow Escape key
    if (event.which == 27) {
        return true;
    }

    return false;
}
