-- Pandoc Lua filter to extend headings.
-- Adds IDs and classes to header elements.

-- Configuration
local config = {
    max_toc_depth = 6,
    debug = false
}

-- State variables
local current_section = ""
local heading_counter = {}

-- Debug logging function
function debug_log(msg)
    if config.debug then
        io.stderr:write("[DEBUG] " .. msg .. "\n")
    end
end

-- Initialize heading counters
for i = 1, 6 do
    heading_counter[i] = 0
end

-- Function to increment heading counter and reset lower levels
function increment_heading_counter(level)
    heading_counter[level] = heading_counter[level] + 1

    -- Reset counters for lower levels
    for i = level + 1, 6 do
        heading_counter[i] = 0
    end

    -- Build section number
    local parts = {}
    for i = 1, level do
        if heading_counter[i] > 0 then
            table.insert(parts, tostring(heading_counter[i]))
        end
    end

    return table.concat(parts, ".")
end

-- Function to safely convert element to string
function stringify_element(el)
    if el then
        return pandoc.utils.stringify(el)
    end
    return ""
end

-- Process headers
function Header(el)
    -- Generate an ID from header text
    local base_id = pandoc.utils.stringify(el)

    -- Clean the ID:
    base_id = string.gsub(base_id, "[^%w%-_]", "-") -- Replace non-alphanumeric (allow _, -) with hyphen
    base_id = string.gsub(base_id, "%-+", "-")      -- Collapse multiple hyphens
    base_id = string.gsub(base_id, "^%-+", "")      -- Remove leading hyphens
    base_id = string.gsub(base_id, "%-+$", "")      -- Remove trailing hyphens
    base_id = string.lower(base_id)

    -- Set the identifier attribute if base_id is not empty
    if base_id ~= "" then
        el.identifier = base_id
    end

    -- Add a class indicating the section level
    if not el.classes then
        el.classes = pandoc.List({}) -- Initialize classes if it's nil
    end
    el.classes:insert("section-level-" .. el.level)

    return el
end

-- Process divs to find requirements (simplified)
function Div(el)
    -- Check if this div has the requirement class
    if el.classes and el.classes:includes("requirement") then
        local text = stringify_element(el)
        debug_log("Found requirement div: " .. text:sub(1, 50) .. "...")
    end

    return el
end

-- Process paragraphs to find potential requirements
function Para(el)
    local text = stringify_element(el)

    -- Look for requirement patterns
    if string.find(text:lower(), "shall") or
       string.find(text:lower(), "must") or
       string.find(text:lower(), "will") then
        debug_log("Found potential requirement: " .. text:sub(1, 50) .. "...")
    end

    return el
end

-- Final document processing
function Pandoc(doc)
    debug_log("Document processing complete")
    return doc
end

-- Return the filter functions
return {
    { Header = Header },
    { Div = Div },
    { Para = Para },
    { Pandoc = Pandoc }
}
