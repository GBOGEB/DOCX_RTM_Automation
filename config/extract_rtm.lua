-- RTM data extraction Lua filter
-- This specialized filter extracts requirement information from Markdown documents

-- Configuration
local config = {
    debug = false,
    rtm_output_file = "output/extracted_rtm.json",
    requirement_patterns = {
        "([Rr]eq%-?%d+)%s*(.+)",  -- Req-123 format
        "([Rr]equirement%s*%d+)%s*(.+)",  -- Requirement 123 format
        "QQQ%-?(%d+)%s*(.+)",  -- QQQ-123 format
        ".*shall%s+(.+)",  -- "shall" statement
        ".*must%s+(.+)"    -- "must" statement
    },
    metadata_patterns = {
        "%[([%w_-]+):([^%]]+)%]"  -- [key:value] format
    }
}

-- State tracking
local current_section = ""
local section_hierarchy = {}
local section_level = 0
local requirements = {}

-- Debug output function
local function debug(msg)
    if config.debug then
        io.stderr:write("[DEBUG] " .. msg .. "\n")
    end
end

-- Extract metadata from text using patterns
local function extract_metadata(text)
    local metadata = {}
    local clean_text = text
    
    for _, pattern in ipairs(config.metadata_patterns) do
        for key, value in string.gmatch(text, pattern) do
            -- Store the metadata
            metadata[string.lower(key)] = string.gsub(value, "^%s+", "")
            metadata[string.lower(key)] = string.gsub(metadata[string.lower(key)], "%s+$", "")
            
            -- Remove the pattern from clean text
            clean_text = string.gsub(clean_text, "%[" .. key .. ":" .. value .. "%]", "")
        end
    end
    
    -- Clean up whitespace
    clean_text = string.gsub(clean_text, "^%s+", "")
    clean_text = string.gsub(clean_text, "%s+$", "")
    
    return metadata, clean_text
end

-- Process headers to track document structure
function Header(elem)
    local level = elem.level
    local text = pandoc.utils.stringify(elem)
    
    -- Reset hierarchy at deeper levels
    for i = level + 1, 6 do
        section_hierarchy[i] = nil
    end
    
    -- Extract or generate section number
    local section_number, header_text = string.match(text, "^([%d%.]+)%s+(.*)")
    if section_number then
        -- Section number is present in the text
        header_text = header_text or ""
        
        -- Parse section number into hierarchy
        local parts = {}
        for num in string.gmatch(section_number, "%d+") do
            table.insert(parts, tonumber(num))
        end
        
        -- Update hierarchy
        for i = 1, #parts do
            section_hierarchy[i] = parts[i]
        end
    else
        -- No section number in text, generate from hierarchy
        header_text = text
        section_hierarchy[level] = (section_hierarchy[level] or 0) + 1
        
        -- Build section number from hierarchy
        section_number = ""
        for i = 1, level do
            if section_hierarchy[i] then
                section_number = section_number .. section_hierarchy[i]
                if i < level then section_number = section_number .. "." end
            end
        end
    end
    
    -- Update current section tracking
    current_section = section_number .. " " .. header_text
    section_level = level
    
    debug("Section: " .. current_section)
    
    return elem
end

-- Extract requirements from paragraphs
function Para(elem)
    local text = pandoc.utils.stringify(elem)
    
    -- Try each requirement pattern
    for _, pattern in ipairs(config.requirement_patterns) do
        local req_id, req_text = string.match(text, pattern)
        
        if req_id and req_text then
            -- Extract any metadata from the text
            local metadata, clean_text = extract_metadata(req_text)
            
            -- Create requirement object
            local requirement = {
                id = req_id,
                text = clean_text or req_text,
                section = current_section,
                level = section_level,
                metadata = metadata
            }
            
            -- Add to requirements list
            table.insert(requirements, requirement)
            
            debug("Found requirement: " .. req_id .. " in section " .. current_section)
            
            -- No need to try other patterns
            break
        end
    end
    
    -- Also check the whole paragraph for requirement indicators
    if text:find(" shall ") or text:find(" must ") then
        -- This looks like a requirement but wasn't caught by the patterns
        -- Let's check if it's inside a div with class="requirement"
        if elem.classes and elem.classes:includes("requirement") then
            -- Extract metadata
            local metadata, clean_text = extract_metadata(text)
            
            -- Generate ID if not found
            local req_id = "REQ-AUTO-" .. #requirements
            if metadata["id"] then
                req_id = metadata["id"]
                metadata["id"] = nil  -- Remove from metadata to avoid duplication
            end
            
            -- Create requirement object
            local requirement = {
                id = req_id,
                text = clean_text or text,
                section = current_section,
                level = section_level,
                metadata = metadata
            }
            
            -- Add to requirements list
            table.insert(requirements, requirement)
            
            debug("Found requirement div: " .. req_id .. " in section " .. current_section)
        end
    end
    
    return elem
end

-- Process divs that might contain requirements
function Div(elem)
    if elem.classes:includes("requirement") then
        local text = pandoc.utils.stringify(elem)
        
        -- Extract metadata
        local metadata = {}
        for key, value in pairs(elem.attributes) do
            metadata[key] = value
        end
        
        -- Get or generate ID
        local req_id = metadata["data-requirement-id"] or "REQ-DIV-" .. #requirements
        if metadata["data-requirement-id"] then
            metadata["data-requirement-id"] = nil  -- Remove to avoid duplication
        end
        
        -- Create requirement object
        local requirement = {
            id = req_id,
            text = text,
            section = current_section,
            level = section_level,
            metadata = metadata
        }
        
        -- Add to requirements list
        table.insert(requirements, requirement)
        
        debug("Found requirement div element: " .. req_id)
    end
    
    return elem
end

-- Process document and save RTM data
function Pandoc(doc)
    -- Extract metadata from document
    local doc_metadata = {}
    if doc.meta then
        for k, v in pairs(doc.meta) do
            if type(v) == "table" and v.t and v.t == "MetaInlines" then
                doc_metadata[k] = pandoc.utils.stringify(v)
            elseif type(v) == "string" then
                doc_metadata[k] = v
            end
        end
    end
    
    -- Prepare RTM data
    local rtm_data = {
        metadata = {
            title = doc_metadata.title or "Untitled Document",
            date = doc_metadata.date or os.date("%Y-%m-%d"),
            version = doc_metadata.version or "1.0",
            generated = os.date("%Y-%m-%d %H:%M:%S"),
            total_requirements = #requirements
        },
        requirements = requirements
    }
    
    -- Write RTM data to JSON file
    local output_dir = string.match(config.rtm_output_file, "(.+)/[^/]+$")
    if output_dir then
        os.execute("mkdir -p " .. output_dir)
    end
    
    -- For Windows, ensure directory exists
    os.execute("if not exist \"" .. output_dir .. "\" mkdir \"" .. output_dir .. "\"")
    
    local output_file = io.open(config.rtm_output_file, "w")
    if output_file then
        -- Convert table to JSON
        local json = pandoc.json.encode(rtm_data)
        output_file:write(json)
        output_file:close()
        debug("Wrote RTM data to " .. config.rtm_output_file)
    else
        debug("Failed to write RTM data")
    end
    
    return doc
end

-- Return the filter
return {
    { Header = Header },
    { Para = Para },
    { Div = Div },
    { Pandoc = Pandoc }
}
