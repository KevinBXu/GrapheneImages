using Gridap
using GridapGmsh

# Clockwise means clockwise from red to green
clockwise = true

model = GmshDiscreteModel("./MoSe2BNMoSe2/Moire_MoSe.msh")
writevtk(model, "Moire")

const ν = 0.0
const λ = ν / ((1+ν)*(1-2ν))
const μ = 1/(2(1+ν))
σ(ε) = λ*tr(ε)*one(ε) + 2μ*ε

order = 2
reffe = ReferenceFE(lagrangian, VectorValue{2,Float64}, order)
V0 = TestFESpace(model, reffe; conformity=:H1)
U0 = TrialFESpace(V0)

degree = 2order
Ω = Triangulation(model)
dΩ = Measure(Ω, degree)

# Basis vectors and reciprocal basis
r =  [0.0728, -0.0783]

if clockwise
  g = [-1/2 √3/2; -√3/2 -1/2]*r
  b = [-1/2 -√3/2; √3/2 -1/2]*r
else
  g = [-1/2 -√3/2; √3/2 -1/2]*r
  b = [-1/2 √3/2; -√3/2 -1/2]*r
end

r⊥ = [0 1; -1 0] * r; r⊥ = r⊥ / (r⊥⋅b)
g⊥ = [0 1; -1 0] * g; g⊥ = g⊥ / (g⊥⋅r)
b⊥ = [0 1; -1 0] * b; b⊥ = b⊥ / (b⊥⋅g)


lines = Dict("red" => 0:1, "green" => -5:1, "blue" => 0:5)
dir = Dict("red" => VectorValue(r⊥),
           "green" => VectorValue(g⊥),
           "blue" => VectorValue(b⊥))

dl = Dict{Tuple{String,Int64},Measure}()
for (t, rge) in lines, i = rge
  L = BoundaryTriangulation(model, tags=["$t $i"])
  dl[t,i] = Measure(L, degree)
end

β = 10 / norm(r⊥)
a(u,v) = ∫( ε(v) ⊙ (σ∘ε(u)) ) * dΩ +([∫( β*(u⋅dir[t])*(v⋅dir[t]) ) * dl[t,i] for (t,i) in keys(dl)]...)
l(v) = +([∫( -β*i*(v⋅dir[t]) ) * dl[t,i] for (t,i) in keys(dl)]...)



op = AffineFEOperator(a,l,U0,V0)

ls = LUSolver()
solver = LinearFESolver(ls)
uh = solve(solver, op)

γ = 1.0
a1(u,v) = ∫( ε(v) ⊙ (σ∘ε(u)) + γ * v⋅u) * dΩ
l1(v) = ∫( γ * v⋅uh) * dΩ

op = AffineFEOperator(a1,l1,U0,V0)
u1h = solve(solver, op)

l2(e) = sqrt(sum(∫(e⋅e)*dΩ))
@show l2(uh - u1h) / l2(uh)

# Differential operators extracting the stress components.
twist(f) = Operation(grad2twist)(∇(f))
function evaluate!(cache,::Broadcasting{typeof(twist)},f)
  Broadcasting(Operation(twist))(Broadcasting(∇)(f))
end
@inline function grad2twist(∇u::TensorValue{2})
  .5(∇u[2,1] - ∇u[1,2])
end

shear(f) = Operation(grad2shear)(∇(f))
function evaluate!(cache,::Broadcasting{typeof(shear)},f)
  Broadcasting(Operation(shear))(Broadcasting(∇)(f))
end
@inline function grad2shear(∇u::TensorValue{2})
  .5(∇u[2,1] + ∇u[1,2])
end

isotropic(f) = Operation(grad2isotropic)(∇(f))
function evaluate!(cache,::Broadcasting{typeof(isotropic)},f)
  Broadcasting(Operation(isotropic))(Broadcasting(∇)(f))
end
@inline function grad2isotropic(∇u::TensorValue{2})
  .5(∇u[1,1] + ∇u[2,2])
end

uniaxial(f) = Operation(grad2uniaxial)(∇(f))
function evaluate!(cache,::Broadcasting{typeof(uniaxial)},f)
  Broadcasting(Operation(uniaxial))(Broadcasting(∇)(f))
end
@inline function grad2uniaxial(∇u::TensorValue{2})
  .5(∇u[1,1] - ∇u[2,2])
end



writevtk(Ω,"./MoSe2BNMoSe2/results_flipped_chirality",cellfields=["u"=>u1h, # "uh"=>uh, "urh"=>uh⋅dir["red"],
      "ur"=>u1h⋅dir["red"],  "ug"=>u1h⋅dir["green"], "ub"=>u1h⋅dir["blue"],
      "twist"=>twist(u1h),"shear"=>shear(u1h),"isotropic"=>isotropic(u1h),"uniaxial"=>uniaxial(u1h)])


nothing