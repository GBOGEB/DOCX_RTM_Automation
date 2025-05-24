
 extracts document structure

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
    local level = el.level
    local title = stringify_element(el)
    
    debug_log("Processing header level " .. level .. ": " .. title)
    
    -- Check if title already has a number
    local has_number = string.match(title, "^%d+[%.%d]*")
    
    if not has_number then
        -- Generate section number
        local section_num = increment_heading_counter(level)
        current_section = section_num
        
        -- Add section number to title
        local new_title = section_num .. " " .. title
        debug_log("Added section number: " .. new_title)
        
        -- Create new header content
        local new_content = {}
        table.insert(new_content, pandoc.Str(new_title))
        
        -- Return modified header
        return pandoc.Header(level, new_content, el.attr)
    else
        debug_log("Header already has numbering: " .. title)
        return el
    end
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
