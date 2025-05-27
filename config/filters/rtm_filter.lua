-- RTM (Requirements Traceability Matrix) Pandoc Lua Filter
-- This filter assists in identifying and marking potential requirements
-- and tracking document sections for easier traceability.

-- Global variable to store the current section context.
-- This is a common pattern in Pandoc Lua filters for passing state between element processors.
current_section = {
    level = 0,
    content = "N/A",
    number = "N/A"
}

-- Function to identify potential requirements based on keywords or patterns.
-- It wraps the identified paragraph in a Div with class "requirement".
function identify_requirements(elem)
    -- Process only Paragraph elements
    if elem.t == "Para" then
        local content = pandoc.utils.stringify(elem)

        -- Check for common requirement indicators (case-insensitive for keywords).
        -- This pattern can be extended for more specific requirement formats.
        if content:lower():match("[Rr]equirement") or content:lower():match("shall") or content:lower():match("must") then
            -- Add a div with class "requirement" around the paragraph for identification.
            -- This allows for easier styling or further processing (e.g., via CSS or other scripts).
            return pandoc.Div(elem, {class = "requirement"})
        end
    end
    -- Return the element unchanged if it's not a requirement or not a Paragraph.
    return elem
end

-- Function to track document sections based on Headers.
-- It updates the global `current_section` variable and adds metadata to Header elements.
function track_sections(elem)
    -- Process only Header elements
    if elem.t == "Header" then
        -- Store the current section details in the global variable.
        current_section = {
            level = elem.level,
            content = pandoc.utils.stringify(elem),
            -- Attempt to extract a section number if headings are numbered (e.g., "1.2.3 Section Title").
            -- The pattern matches digits, dots, and then captures the number.
            number = pandoc.utils.stringify(elem):match("^(%d[%d%.]*)")
        }

        -- Add section metadata as attributes to the Header element.
        -- These attributes can be used by other scripts or for styling.
        elem.attributes["data-section-number"] = current_section.number or "" -- Use extracted number or empty string
        elem.attributes["data-section-title"] = current_section.content
        elem.attributes["data-section-level"] = tostring(current_section.level)
    end
    -- Return the element, possibly modified with new attributes.
    return elem
end

-- Return the list of filter functions.
-- Pandoc will apply these functions to the document elements in the order they are listed.
-- `track_sections` should ideally run before `identify_requirements` if requirement processing
-- needs to know the current section, though in this specific setup, they are independent.
return {
    track_sections,
    identify_requirements
}
