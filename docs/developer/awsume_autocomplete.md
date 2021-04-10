# Awsume Autocomplete

This logic has been broken into a separate module to help speed up the execution time of the autocomplete script. Instead of invoking `awsume` when a shell needs to autocomplete an awsume command (which spends a lot of time initializing the plugin manager and loading package utils), the shell invokes `awsume-autocomplete`.

We're also using the [`fastentrypoints`](https://github.com/ninjaaron/fast-entry_points) package to help speed things up even more.

Because we're not using the plugin manager for awsume's autocomplete, we use a cache of profile names so that we can still autocomplete plugin-provided profile names. This is great because autocomplete times have been drastically reduced, but is unfortunate in that for plugins for which the set of returned profiles changes, `awsume --refresh-autocomplete` must be run in order to get the latest set of profiles.
