-- Document Structure Extraction Lua filter for Pandoc
-- This filter extracts the document structure during conversion from DOCX to Markdown

-- Configuration
local config = {
    output_file = "output/document_structure_raw.json",
    extract_requirements = true,
    extract_dependencies = true,
    debug = false
}

-- State variables
local document_title = ""
local current_section = ""
local current_level = 0
local headings = {}
local requirements = {}
local dependencies = {}

-- Debug logging
function debug(msg)
    if config.debug then
        io.stderr:write("[DEBUG] " .. msg .. "\n")
    end
end

-- Convert Pandoc element to plain text
function to_plain_text(el)
    if el then
        return pandoc.utils.stringify(el)
    end
    return ""
end

-- Process headers to extract structure
function Header(el)
    local level = el.level
    local title = to_plain_text(el)
    
    -- Check for section number at the beginning
    local section_num, clean_title = string.match(title, "^(%d+[%d%.%s]*)%s*(.*)")
    
    if not section_num then
        clean_title = title
    end
    
    -- Check for LCP phase annotation
    local lcp_phase = string.match(clean_title, "%[LCP:(%d+)%]")
    local final_title = lcp_phase and string.gsub(clean_title, "%[LCP:%d+%]", ""):gsub("%s+$", "") or clean_title
    
    -- Store heading
    table.insert(headings, {
        level = level,
        section = section_num or "",
        title = final_title,
        lcp_phase = lcp_phase or ""
    })
    
    -- Update current section and level
    current_section = section_num or ""
    current_level = level
    
    -- If this is the first level 1 heading, assume it's the document title
    if level == 1 and #headings == 1 then
        document_title = final_title
    end
    
    debug("Extracted heading: " .. (section_num or "") .. " " .. final_title)
    
    return el
end

-- Process divs to find requirements
function Div(el)
    -- Check if this div has the requirement class
    if el.classes:includes("requirement") then
        -- Extract requirement text
        local text = to_plain_text(el)
        
        -- Try to extract requirement ID
        local req_id = string.match(text, "([Rr][Ee][Qq]%-?%d+)")
        if not req_id then
            req_id = "REQ-AUTO-" .. #requirements + 1
        end
        
        -- Extract metadata tags [key:value]
        local metadata = {}
        local clean_text = text
        for key, value in string.gmatch(text, "%[([%w_-]+):([^%]]+)%]") do
            metadata[string.lower(key)] = value:gsub("^%s+", ""):gsub("%s+$", "")
            clean_text = clean_text:gsub("%[" .. key .. ":" .. value .. "%]", "")
        end
        
        -- Store requirement
        table.insert(requirements, {
            id = req_id,
            text = clean_text:gsub("^" .. req_id .. "%s*", ""):gsub("^%s+", ""):gsub("%s+$", ""),
            section = current_section,
            level = current_level,
            metadata = metadata
        })
        
        debug("Extracted requirement: " .. req_id)
    end
    
    return el
end

-- Process paragraphs to find implicit requirements or dependencies
function Para(el)
    local text = to_plain_text(el)
    
    -- Look for requirement statements
    if config.extract_requirements and (
        string.find(text:lower(), "shall") or 
        string.find(text:lower(), "must") or
        string.find(text:lower(), "will")
    ) then
        -- Extract requirement ID if present or generate auto-ID
        local req_id = string.match(text, "([Rr][Ee][Qq]%-?%d+)")
        if not req_id and (not el.classes or not el.classes:includes("requirement")) then
            req_id = "REQ-IMPLIED-" .. #requirements + 1
            
            -- Store the requirement
            table.insert(requirements, {
                id = req_id,
                text = text,
                section = current_section,
                level = current_level,
                metadata = {
                    implied = "true"
                }
            })
            
            debug("Extracted implicit requirement: " .. req_id)
        end
    end
    
    -- Look for dependency statements
    if config.extract_dependencies then
        -- Look for patterns like "REQ-001 depends on REQ-002"
        for source_id, rel_type, target_id in string.gmatch(text, "([Rr][Ee][Qq]%-?%d+)%s+([%w%s_]+)%s+([Rr][Ee][Qq]%-?%d+)") do
            rel_type = rel_type:lower()
            if rel_type == "depends on" then
                rel_type = "depends_on"
            elseif rel_type == "related to" then
                rel_type = "related_to"
            end
            
            table.insert(dependencies, {
                source = source_id,
                target = target_id,
                type = rel_type
            })
            
            debug("Extracted dependency: " .. source_id .. " " .. rel_type .. " " .. target_id)
        end
    end
    
    return el
end

-- Process the entire document at the end
function Pandoc(doc)
    -- Save the extracted structure
    local structure = {
        title = document_title,
        headings = headings,
        requirements = requirements,
        dependencies = dependencies
    }
    
    -- Ensure existence of output directory
    local output_dir = string.match(config.output_file, "^(.+)/[^/]+$")
    if output_dir then
        os.execute("mkdir -p " .. output_dir)
    end
    
    -- Write to JSON file (use simple JSON encoding instead of pandoc.json.encode)
    local function simple_json_encode(obj)
        if type(obj) == "string" then
            return '"' .. obj:gsub('"', '\\"') .. '"'
        elseif type(obj) == "number" then
            return tostring(obj)
        elseif type(obj) == "table" then
            if #obj > 0 then
                -- Array
                local items = {}
                for i, v in ipairs(obj) do
                    table.insert(items, simple_json_encode(v))
                end
                return "[" .. table.concat(items, ",") .. "]"
            else
                -- Object
                local items = {}
                for k, v in pairs(obj) do
                    table.insert(items, '"' .. k .. '":' .. simple_json_encode(v))
                end
                return "{" .. table.concat(items, ",") .. "}"
            end
        else
            return '""'
        end
    end
    
    local json = simple_json_encode(structure)
    local file = io.open(config.output_file, "w")
    if file then
        file:write(json)
        file:close()
        debug("Wrote document structure to " .. config.output_file)
    else
        debug("Failed to write document structure")
    end
    
    return doc
end

-- Return the filter
return {
    { Header = Header },
    { Div = Div },
    { Para = Para },
    { Pandoc = Pandoc }
}

<div class="caption">Figure 1: Pipeline Architecture</div>

## 6.2 Module Structure [LCP:2]

<div class="requirement">
REQ-049 The system shall implement a modular design with well-defined interfaces between components. [priority:high] [status:implemented]
</div>

The system is organized into the following module structure:

<div class="caption">Figure 2: Module Structure</div>

# 7 Appendices

## 7.1 Glossary

| Term | Definition |
|:-----|:-----------|
| DOCX | Microsoft Word Open XML Document format |
| RTM  | Requirements Traceability Matrix - A document that maps requirements to their implementation and verification |
| Pandoc | A universal document converter |
| LCP | Life Cycle Phase - Project phase where a requirement should be implemented |
| YAML | YAML Ain't Markup Language - A human-friendly data serialization standard |

## 7.2 Sample Requirements

The following is a sample of how requirements should be formatted in input documents:
