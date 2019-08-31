# Fuzzy Matching

If enabled in awsume's [global config](../general/config), awsume will attempt to fuzzy match your profile name to an available profile if the given profile name is not found.

There are three methods used to match a profile name to a given profile (in order):

- Prefix Match
- Longest Contains
- Levenshtein Distance

For each method, if there is one closest profile, that is the profile that will be chosen. If there is a tie for which profile is closest, no profile will be returned.

## Prefix Match

Compare the given profile name to each profile as if it was the prefix.

For example, if these are your profiles:

```
dev-readonly
dev-admin
```

- `dev-a` would match to the `dev-admin` profile
- `dev` would not match to any profile

## Longest Contains

Compare the longest common sequence of characters between the given profile name and each profile.

For example, if these are your profiles:

```
hello-dev-readonly
goodbye-dev-readonly
```

- `dev-readonly` would not match to any profile
- `bye-dev-read` would match to the `goodbye-dev-readonly` profile

## Levenshtein Distance

Compare the given profile name to each profile with the [levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance). This is useful mainly for small typos.

For example, if these are your profiles:

```
dev-readonly
dev-admin
profile1
profile2
```

- `dev-admib` would match to `dev-admin`
- `profile` would not match to any, since the levenshtein distance between both `profile1` and `profile2` and the given `profile` is the same
