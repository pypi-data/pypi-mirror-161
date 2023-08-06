# Replacing schematics
#
# We definitely want to get rid of Schematics 1. Schematics 2 isn't much better (actually worse in some cases, like conversion without validation), IMHO the reasonable alternatives are:
#
# * https://github.com/petee-d/stereotype
#   - my library created specifically for this purpose, 3 stars, surprisingly
#   - compared to schematics: ~11x faster conversion, ~45x faster with validation, ~4.93 less memory usage
#   - compatible with how we use schematics
# * https://pydantic-docs.helpmanual.io/
#   - 9k stars on GitHub
#   - compared to stereotype: 1.12x slower conversion, ~2.59x slower with validation, uses 1.86x more memory
#   - IMHO uglier validation, since last year finally can separate validation from conversion
# * https://www.attrs.org/en/stable/
#   - 4k stars on GitHub
#   - compared to stereotype: ~1.27x slower conversion, slightly faster with validation, uses ~ same memory
#   - recursive models are very ugly, has problems with inheritance from models with defaults, cannot convert without validating
#
# Let's discuss the pros and cons in more detail, choose the right replacement and discuss how it could be done.