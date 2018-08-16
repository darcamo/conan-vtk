from cpt.packager import ConanMultiPackager

if __name__ == "__main__":
    builder = ConanMultiPackager(username="darcamo", channel="stable")
    builder.add_common_builds(pure_c=False)

    filtered_builds = []
    for settings, options, env_vars, build_requires, reference in builder.items:
        if settings["compiler.libcxx"] != "libc++":  # libc++ from clang does not have algorithm header
            filtered_builds.append([settings, options, env_vars, build_requires])
    builder.builds = filtered_builds

    builder.run()
