def get_displayable_string(s, col_width):
    """Format a string to a given column width
    @param s string that can represent an integer, float, or text
    @param col_width desired number of characters
    @return the string formatted to desired width otherwise a string of hashes"""
    try:
        # Does the string fit?
        if len(s) <= col_width:
            return s  #it's fine as it is
        # If it's too long, see if it's a float we can shorten
        # Check if it's a valid float but not an integer
        if '.' in s:
            # If the number has decimals, check the number of leading digits
            # Try to convert the string to a float
            num = float(s)
            # get leading digits length
            lead_digits = len(s.split('.')[0])
            # if leading digits > colwidth use "####'
            if lead_digits > col_width:
                return '#' * col_width
            # if leading digits = colwidth Use .0f
            if lead_digits == col_width:
                precision = 0  # You can change this to any desired number of decimal places
            else:  #(leading digits < colwidth)
                precision = col_width - (lead_digits+1)   #Use .xf
            formatted_str = f"{num:.{precision}f}"
            return formatted_str
        else: #reject integers
            raise ValueError
    except ValueError:
        # the string is not a valid float or it's too long
        return '#' * col_width  # Return the hash string if it's too long

if __name__ == '__main__':
    assert (f"{1234.5432:.0f}") == "1235"    # 4 columns
    assert (f"{123.456:.0f}") == "123"    # 3 columns
    assert (f"{12.34356:.1f}") == "12.3"    # 4 columns
    assert (f"{1.234356:.2f}") == "1.23"    # 4 columns
    # Example of a string that will #####
    assert (f"{123.456:.1f}") == "123.5"  # 5 columns  *Note there's no 4 columns because "123." doesn't make sense.

    print ("Starting Calc-like tests")
    assert get_displayable_string("123.456",4) == "123"
    assert get_displayable_string("123",4) == "123"
    assert get_displayable_string("1234",4) == "1234"
    assert get_displayable_string("123",4) == "123"
    assert get_displayable_string("12.3435678",4) == "12.3"
    assert get_displayable_string("1234.5432",4) == "1235"
    assert get_displayable_string("1.2345",4) == "1.23"

    # Test cases
    assert get_displayable_string("123",10) == "123"
    assert get_displayable_string("123456789", 5) == "#####"
    assert get_displayable_string("12345.6789", 10) == "12345.6789"
    assert get_displayable_string("12345.6789", 5) == "12346"
    assert get_displayable_string("12345.6", 10) ==  "12345.6"
    assert get_displayable_string("hello world", 5) == "#####"
    assert get_displayable_string("hello", 8) == "hello"
    assert get_displayable_string("123", 5) == "123"
    assert get_displayable_string("123456789", 5) == "#####"
    # Notice f"{num:.2f}" rounds two 2 decimal places
    assert get_displayable_string("100013.6789", 9) == "100013.68"

