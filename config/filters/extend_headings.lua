-- Pandoc Lua Filter: Extend Headings
-- This filter automatically numbers document headings (e.g., H1, H2, H3)
-- if they are not already numbered. It also includes example functions
-- for debugging or simple content analysis within Divs and Paragraphs.

-- Configuration table for the filter
local config = {
    max_toc_depth = 6, -- Maximum heading level to number
    debug = false      -- Enable/disable debug logging to stderr
}

-- State variables
-- `current_section` stores the last generated section number (mainly for debug/reference).
local current_section = ""
-- `heading_counter` keeps track of the current number for each heading level.
local heading_counter = {}

-- Debug logging function: prints messages to stderr if config.debug is true.
function debug_log(msg)
    if config.debug then
        io.stderr:write("[DEBUG extend_headings.lua] " .. msg .. "\n")
    end
end

-- Initialize heading counters for each level up to max_toc_depth.
for i = 1, config.max_toc_depth do
    heading_counter[i] = 0
end

-- Function to increment heading counter for the given level
-- and reset counters for all lower (deeper) levels.
-- Returns the generated section number string (e.g., "1.2.1").
function increment_heading_counter(level)
    -- Ensure level is within bounds
    if level < 1 or level > config.max_toc_depth then
        return "" -- Or handle error
    end

    heading_counter[level] = heading_counter[level] + 1

    -- Reset counters for lower levels to ensure correct sub-numbering (e.g., after 1.1, next H2 is 1.2, not 1.1.1 continuing from a previous H3).
    for i = level + 1, config.max_toc_depth do
        heading_counter[i] = 0
    end

    -- Build section number string (e.g., "1" for H1, "1.2" for H2, "1.2.3" for H3)
    local parts = {}
    for i = 1, level do
        if heading_counter[i] > 0 then
            table.insert(parts, tostring(heading_counter[i]))
        else
            -- This case should ideally not happen if levels are sequential.
            -- For robustness, one might add a '0' or skip.
            -- table.insert(parts, "0")
        end
    end

    return table.concat(parts, ".")
end

-- Function to safely convert an element's content to a string.
function stringify_element(el)
    if el and el.content then -- Check if el.content exists
        return pandoc.utils.stringify(el)
    elseif type(el) == 'string' then -- el itself might be a string
        return el
    end
    return "" -- Return empty string if el or el.content is nil
end

-- Process Header elements to add numbering.
function Header(el)
    local level = el.level
    -- Use stringify_element for safety, as el.content might be complex.
    local title_text = pandoc.utils.stringify(el) -- Get the raw text content of the header

    debug_log("Processing header level " .. level .. ": " .. title_text)

    -- Check if the title already starts with a number (e.g., "1. Introduction", "2.1. Method").
    -- The pattern `^%s*%d+[%.%d]*` looks for optional leading spaces, then digits and dots.
    local has_number = string.match(title_text, "^%s*%d+[%.%d]*")

    if not has_number and level <= config.max_toc_depth then
        -- Generate section number if not already numbered and within max depth.
        local section_num = increment_heading_counter(level)
        current_section = section_num -- Update global current_section (mainly for reference/debug)

        -- Prepend the section number to the original title.
        local new_title_content = {pandoc.Str(section_num .. " ")}
        -- Append original header content after the number
        for _, inline_el in ipairs(el.content) do
            table.insert(new_title_content, inline_el)
        end

        debug_log("Added section number: " .. section_num .. " to title: " .. title_text)

        -- Return a new Header element with the modified content and original attributes.
        return pandoc.Header(level, new_title_content, el.attr)
    else
        if has_number then
            debug_log("Header already has numbering: " .. title_text)
        else
            debug_log("Header level " .. level .. " exceeds max_toc_depth of " .. config.max_toc_depth .. ". Not numbering.")
        end
        -- Return the element unchanged if already numbered or exceeds max depth.
        return el
    end
end

-- Example function to process Div elements.
-- In this filter, it's primarily for demonstration or debugging.
-- It could be extended to interact with numbered sections if needed.
function Div(el)
    -- Check if this div has a specific class, e.g., "requirement" (as in rtm_filter.lua).
    if el.classes and el.classes:includes("requirement") then
        local text = stringify_element(el)
        debug_log("Found div with class 'requirement': " .. text:sub(1, 50) .. "...")
        -- Could add current_section info here if relevant:
        -- el.attributes['data-parent-section'] = current_section
    end

    return el
end

-- Example function to process Paragraph elements.
-- In this filter, it's primarily for demonstration or debugging.
-- It could be used for simple keyword spotting within paragraphs.
function Para(el)
    local text = stringify_element(el)

    -- Example: Look for specific keywords in paragraphs.
    if string.find(text:lower(), "shall") or
       string.find(text:lower(), "must") or
       string.find(text:lower(), "will") then
        debug_log("Found potential requirement keyword in Para: " .. text:sub(1, 70) .. "...")
        -- Could wrap this in a Span or Div, or add attributes, if needed.
    end

    return el
end

-- Function called once after the entire document has been processed.
-- Useful for final cleanups or summary generation (not used here).
function Pandoc(doc)
    debug_log("Document processing with extend_headings.lua complete.")
    return doc
end

-- Return the filter functions to be applied by Pandoc.
-- The order matters if functions depend on modifications made by previous ones.
return {
    { Header = Header }, -- Process Headers first for numbering
    { Div = Div },       -- Then process Divs
    { Para = Para },     -- Then process Paragraphs
    { Pandoc = Pandoc }  -- Finally, the Pandoc function for the whole document
}
