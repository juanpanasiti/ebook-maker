-- syntax-alias.lua
-- Maps unsupported languages (like rego) to supported ones for Pandoc native syntax highlighting

local alias_map = {
    -- julia supports '#' comments and has keywords like 'in', as well as ':=' operator, 
    -- making it visually a much better fit for Rego syntax highlighting than Go.
    rego = "julia",
    -- Add more unsupported languages here if needed
}

function CodeBlock(el)
    if el.classes and #el.classes > 0 then
        local lang = el.classes[1]
        local mapped_lang = alias_map[string.lower(lang)]
        
        if mapped_lang then
            -- Replace the first class (the language) with the mapped alias
            el.classes[1] = mapped_lang
            return el
        end
    end
end
