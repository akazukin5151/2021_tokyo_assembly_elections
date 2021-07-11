// Scraps data from
// https://www.yomiuri.co.jp/election/local/togisen2021/kouho/
// Output is raw_results.json

// Set temp0 to the element with class = "uni-election-local-2021 local-2021-kouho"
// And run in Browser Console

const header = "election-local-2021-brief-section-person-header result"
const nv = "election-local-2021-brief-section-person-number-of-votes"
const party = "election-local-2021-brief-section-person__party"

// let temp0 =

// districts :: [[[HTML]]]
let districts = Array.from(temp0.children).slice(4, 46)

// Votes received and political party
// data Result = Map String String

// data DistrictName = String
// data Nested = Result | DistrictName

// main :: [[[HTML]]] -> [Map String Nested]
function main(districts) {
    let res = []
    for (let district of districts) {
        let name = district.children[0].children[0].innerText
        let cands = district.children[1].children
        res.push({name: name, results: map_cands(cands)})
    }
    return res  // output
}

// map_cands :: [[HTML]] -> [Result]
function map_cands(cands) {
    let res = []
    for (let cand of cands) {
        if (cand.className !== header) {
            res.push(map_col(cand))
        }
    }
    return res
}

// map_col :: [HTML] -> Result
function map_col(cand) {
    let dict = {}
    for (let col of cand.children[0].children) {
        if (col.className === nv) {
            dict.num_votes = col.innerText
        } else if (col.className === party) {
            dict.party = col.innerText
        }
    }
    return dict
}
