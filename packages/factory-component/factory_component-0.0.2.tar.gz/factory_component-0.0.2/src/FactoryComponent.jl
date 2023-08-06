
module FactoryComponent
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.1"

include("jl/example.jl")
include("jl/rnd.jl")
include("jl/texteditor.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "factory_component",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "factory_component.min.js",
    external_url = nothing,
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "factory_component.min.js.map",
    external_url = nothing,
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
