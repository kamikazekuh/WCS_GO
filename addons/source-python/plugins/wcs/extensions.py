"""Module for extended Source.Python's menus with more features."""

# Source.Python
import menus


class PagedMenu(menus.PagedMenu):
    """
    Extend's Source.Python's default menus package with new features
    and functionality, such as
    - constants: Display same option on all pages
    - previous_menu: presssing "Previous" on the first page
    - next_menu: pressing "Next" on the last page
    - display_page_info: Display the page number in top right corner
    """

    def __init__(
            self, data=None, select_callback=None, build_callback=None,
            description=None, title=None, top_separator=None,
            bottom_separator=None, fill=False, constants=None,
            previous_menu=None, next_menu=None, display_page_info=False):
        """Initializes a new PagedMenu instance."""
        if top_separator is None:
            top_separator = '--------------'
        if bottom_separator is None:
            bottom_separator = '--------------'
        super().__init__(
            data, select_callback, build_callback,
            description, title, top_separator, bottom_separator, fill)
        self.constants = constants if constants is not None else {}
        self.previous_menu = previous_menu
        self.next_menu = next_menu
        self.display_page_info = display_page_info

    def _get_max_item_count(self):
        """Returns the maximum possible item count per page."""
        return 6 - len(self.constants)

    def _format_header(self, player_index, page, slots):
        """Prepares the header for the menu."""
        # Create the page info string
        info = ''
        if self.display_page_info:
            info = ' [{0}/{1}]'.format(page.index + 1, self.page_count)

        # Create the buffer
        if self.title:
            buffer = '{0}{1}\n'.format(
                menus.base._translate_text(self.title, player_index), info)
        elif info:
            buffer = '{0}\n'.format(info)
        else:
            buffer = ''

        # Set description if present
        if self.description is not None:
            buffer += menus.base._translate_text(
                self.description, player_index) + '\n'

        # Set the top separator if present
        if self.top_separator is not None:
            buffer += self.top_separator + '\n'

        return buffer

    def _format_body(self, player_index, page, slots):
        """Prepares the body for the menu."""
        buffer = ''

        # Get all the options for the current page
        options = self._get_options(page.index)
        option_iter = iter(options)

        # Loop through numbers from 1 to 6
        choice_index = 0
        while choice_index < 7:

            # Increment the choice index
            choice_index += 1

            # See if there's a constant option for that number
            if choice_index in self.constants:
                option = self.constants[choice_index]

            # Else pick the next option from the page
            else:
                try:
                    option = next(option_iter)
                except StopIteration:
                    continue  # In case there are constants left

            # Add the option to page's options
            page.options[choice_index] = option

            # Add the option's text like SP's PagedMenu does
            if isinstance(option, menus.PagedOption):
                buffer += option._render(player_index, choice_index)
                if option.selectable:
                    slots.add(choice_index)
            else:
                choice_index -= 1
                if isinstance(option, menus.Text):
                    buffer += option._render(player_index, choice_index)
                else:
                    buffer += menus.Text(option)._render(player_index, choice_index)

        if self.fill:
            buffer += ' \n' * (6 - len(options) - len(self.constants))

        return buffer

    def _format_footer(self, player_index, page, slots):
        """Prepares the footer for the menu."""
        buffer = ''

        # Set the bottom separator if present
        if self.bottom_separator is not None:
            buffer += '{0}\n'.format(self.bottom_separator)

        # Add "Previous" option
        option_previous = menus.PagedOption(
            'Back',
            self.previous_menu,
            highlight=False,
            selectable=False)
        if page.index > 0 or self.previous_menu:
            option_previous.highlight = option_previous.selectable = True
            slots.add(7)
        buffer += option_previous._render(player_index, 7)

        # Add "Next" option
        option_next = menus.PagedOption(
            'Next',
            self.next_menu,
            highlight=False,
            selectable=False)
        if page.index < self.last_page_index or self.next_menu:
            option_next.highlight = option_next.selectable = True
            slots.add(8)
        buffer += option_next._render(player_index, 8)

        # Add "Close" option
        option_close = menus.PagedOption(
            'Close',
            highlight=False)
        buffer += option_close._render(player_index, 9)
        slots.add(9)

        # Return the buffer
        return buffer

    def _select(self, player_index, choice_index):
        """Handles a menu selection."""
        page = self._player_pages[player_index]
        if choice_index == 7 and page.index == 0 and self.previous_menu:
            return self.previous_menu
        elif (choice_index == 8 and page.index == self.last_page_index
                and self.next_menu):
            return self.next_menu
        return super()._select(player_index, choice_index)