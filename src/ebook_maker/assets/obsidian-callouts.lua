function BlockQuote(el)
    local first_block = el.content[1]
    if not first_block or first_block.t ~= "Para" then return nil end

    local first_inline = first_block.content[1]
    if not first_inline or first_inline.t ~= "Str" then return nil end

    -- Detect Obsidian callout syntax: [!type] or [!type]+ or [!type]-
    local callout_type = first_inline.text:match("^%[%!(%w+)%][%+%-]?$")

    if callout_type then
        local type_lower = string.lower(callout_type)
        
        -- Map aliases to their base types, as defined in Obsidian
        local alias_map = {
            -- Abstract group
            summary = "abstract", tldr = "abstract",
            -- Info group
            todo = "info",
            -- Tip group
            hint = "tip", important = "tip",
            -- Success group
            check = "success", done = "success",
            -- Question group
            help = "question", faq = "question",
            -- Warning group
            caution = "warning", attention = "warning",
            -- Failure group
            fail = "failure", missing = "failure",
            -- Danger group
            error = "danger", bug = "danger",
            -- Quote group
            cite = "quote"
        }
        
        local mapped_type = alias_map[type_lower] or type_lower
        
        -- Identify the title (rest of the first line)
        table.remove(first_block.content, 1) -- remove the [!type] marker
        
        -- Trim starting space
        if first_block.content[1] and first_block.content[1].t == "Space" then
            table.remove(first_block.content, 1)
        end
        
        local title_inlines = {}
        local has_custom_title = false
        local rest_of_para = {}
        local found_break = false

        for i, inline in ipairs(first_block.content) do
            if inline.t == "SoftBreak" or inline.t == "LineBreak" then
                found_break = true
                for j = i + 1, #first_block.content do
                    table.insert(rest_of_para, first_block.content[j])
                end
                break
            else
                table.insert(title_inlines, inline)
                has_custom_title = true
            end
        end

        if not has_custom_title then
            -- Fallback title: Capitalized type (e.g. "Note")
            table.insert(title_inlines, pandoc.Str(callout_type:gsub("^%l", string.upper)))
        end

        local divs = {}
        
        -- Generate Title div
        table.insert(divs, pandoc.Div(pandoc.Para(title_inlines), pandoc.Attr("", {"admonition-title"})))

        -- Generate Body div
        local body_blocks = {}
        if #rest_of_para > 0 then
            table.insert(body_blocks, pandoc.Para(rest_of_para))
        end
        for i = 2, #el.content do
            table.insert(body_blocks, el.content[i])
        end

        if #body_blocks > 0 then
            table.insert(divs, pandoc.Div(body_blocks, pandoc.Attr("", {"admonition-content"})))
        end

        -- Wrap in the main admonition div
        return pandoc.Div(divs, pandoc.Attr("", {"admonition", "admonition-" .. mapped_type}))
    end
end

-- Fix invalid HTML attribute 'align' that causes Amazon KDP/Epubcheck to reject the EPUB
function RawBlock(el)
    if el.format:match("html") then
        el.text = el.text:gsub('align="right"', 'style="text-align: right;"')
        el.text = el.text:gsub('align="center"', 'style="text-align: center;"')
        el.text = el.text:gsub('align="left"', 'style="text-align: left;"')
        return el
    end
end

function RawInline(el)
    if el.format:match("html") then
        el.text = el.text:gsub('align="right"', 'style="text-align: right;"')
        el.text = el.text:gsub('align="center"', 'style="text-align: center;"')
        el.text = el.text:gsub('align="left"', 'style="text-align: left;"')
        return el
    end
end
