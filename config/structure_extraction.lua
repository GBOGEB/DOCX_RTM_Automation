-- Document Structure Extraction Lua filter for Pandoc
-- This filter extracts the document structure, requirements, and dependencies.

-- Configuration
local config = {
    output_file = "output/document_structure_raw.json",
    extract_requirements = true,
    extract_dependencies = true,
    debug = false -- Set to true for verbose logging to stderr
}

-- State variables
local document_title = ""
local current_section_path = {} -- Stack to keep track of current section path
local headings = {}
local requirements = {}
local dependencies = {}

-- Debug logging function
local function debug(msg)
    if config.debug then
        io.stderr:write("[LUA DEBUG] " .. msg .. "\n")
    end
end

-- Convert Pandoc element to plain text
local function to_plain_text(el)
    if el then
        return pandoc.utils.stringify(el)
    end
    return ""
end

-- Process headers to extract structure
function Header(el)
    local level = el.level
    local title = to_plain_text(el)

    local section_num, clean_title = string.match(title, "^(%d+[%d%.%s]*)%s*(.*)")

    if not section_num then
        clean_title = title
    end

    local lcp_phase = string.match(clean_title, "%[LCP:(%d+)%]")
    local final_title = clean_title
    if lcp_phase then
        final_title = string.gsub(clean_title, "%[LCP:%d+%]", "")
        final_title = string.gsub(final_title, "%s+$", "") -- Trim trailing whitespace
    end

    while #current_section_path >= level do
        table.remove(current_section_path)
    end
    table.insert(current_section_path, final_title)

    table.insert(headings, {
        level = level,
        section_number = section_num or "",
        title = final_title,
        lcp_phase = lcp_phase or "",
        path = table.concat(current_section_path, " / ")
    })

    if level == 1 and #headings == 1 then
        document_title = final_title
    end

    debug("Header: Lvl " .. level .. ", Num " .. (section_num or "N/A") .. ", Title '" .. final_title .. "'")
    return el
end

-- Process divs to find requirements
function Div(el)
    if config.extract_requirements and el.classes and el.classes:includes("requirement") then
        local text_content = to_plain_text(el)

        local req_id = el.attributes.id or string.match(text_content, "([Rr][Ee][Qq]%-?%d+[%w%.%-]*)")
        if not req_id then
            req_id = "REQ-AUTO-" .. (#requirements + 1)
        end

        local metadata = {}
        if el.attributes then
            for k, v in pairs(el.attributes) do
                if k ~= "id" and k ~= "class" then
                     metadata[string.lower(k)] = v
                end
            end
        end

        local clean_text = text_content
        for key, value in string.gmatch(text_content, "%[([%w_-]+):([^%]]+)%]") do
            metadata[string.lower(key)] = value:gsub("^%s+", ""):gsub("%s+$", "")
            clean_text = clean_text:gsub("%[" .. key .. ":" .. value .. "%]", "")
        end

        clean_text = clean_text:gsub("^%s*" .. req_id .. "%s*:%s*", ""):gsub("^%s+", ""):gsub("%s+$", "")

        table.insert(requirements, {
            id = req_id,
            text = clean_text,
            section_path = table.concat(current_section_path, " / "),
            metadata = metadata
        })

        debug("Requirement (Div): ID '" .. req_id .. "', Text '" .. clean_text:sub(1,30) .. "...'")
    end
    return el
end

-- Process paragraphs to find implicit requirements or dependencies
function Para(el)
    local text = to_plain_text(el)

    if config.extract_requirements then
        local req_keywords = {"shall", "must", "will"}
        for _, keyword in ipairs(req_keywords) do
            if string.find(text:lower(), keyword) then
                local req_id_match = string.match(text, "([Rr][Ee][Qq]%-?%d+[%w%.%-]*)")
                if not req_id_match then
                    local req_id = "REQ-IMPLIED-" .. (#requirements + 1)
                    table.insert(requirements, {
                        id = req_id,
                        text = text,
                        section_path = table.concat(current_section_path, " / "),
                        metadata = { implied = "true", source_keyword = keyword }
                    })
                    debug("Implicit Req (Para): ID '" .. req_id .. "', Keyword '" .. keyword .. "'")
                    break
                end
            end
        end
    end

    if config.extract_dependencies then
        for source_id, rel_text, target_id in string.gmatch(text, "([Rr][Ee][Qq]%-?%d+[%w%.%-]*)%s+([%w%s_]+?)%s+([Rr][Ee][Qq]%-?%d+[%w%.%-]*)") do
            local rel_type = string.lower(rel_text):gsub("%s+", "_")

            table.insert(dependencies, {
                source = source_id,
                target = target_id,
                type = rel_type
            })
            debug("Dependency: '" .. source_id .. "' " .. rel_type .. " '" .. target_id .. "'")
        end
    end
    return el
end

-- Process the entire document at the end
function Pandoc(doc)
    local structure = {
        title = document_title,
        headings = headings,
        requirements = requirements,
        dependencies = dependencies
    }

    local output_dir_path = string.match(config.output_file, "^(.+)[/\\][^/\\]+$")
    if output_dir_path then
        os.execute("mkdir -p \"" .. output_dir_path .. "\"")
    else
        os.execute("mkdir -p \"output\"")
    end

    -- Use Pandoc's built-in JSON encoder - THIS IS THE CRITICAL FIX
    local json_content = pandoc.json.encode(structure)

    local file, err = io.open(config.output_file, "w")
    if file then
        file:write(json_content)
        file:close()
        debug("Wrote document structure to " .. config.output_file)
    else
        debug("Failed to write to " .. config.output_file .. ": " .. (err or "unknown error"))
    end

    return doc
end

-- Return the filter table
return {
    { Header = Header },
    { Div = Div },
    { Para = Para },
    { Pandoc = Pandoc }
}
