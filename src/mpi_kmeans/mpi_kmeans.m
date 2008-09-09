function [CX, sse, assignment] = mpi_kmeans(X, initcenters, maxiterations,nr_restarts)

% MPI_KMEANS    K-means clustering
%               [CX, sse] = mpi_kmeans(X, initcenters)
%	or	CX = mpi_kmeans(X, initcenters)
%       or      [CX, sse] = mpi_kmeans(X, initcenters,maxiterations)
%       or      [CX, sse] = mpi_kmeans(X, initcenters,maxiterations,nr_restarts)
%       or      [CX, sse, assignment] = mpi_kmeans(X, ... )
%
%               - X: input points (one per column)
%               - initcenters: 
%			either a scalar: number of clusters
%			otherwise kmeans is initialized at these vectors
%		- maxiterations: maximum number of iterations
%		(default:unlimited), can be Inf
%		- nr_restarts: return the best result (lowest sse) over
%		nr_restart+1 independent runs of the K-kmeans
%		algorithm (default: 0)
%
%               - CX: cluster centers
%               - sse: Sum of Squared Error (faster if not
%               requested)
%		- assignment of points X to nearest cluster center
%
% Example: 
%  X = randn(128,10000);
%   [Cx,sse] = mpi_kmeans(X,50);
%   [Cx,sse] = mpi_kmeans(X,randn(128,50));
%
% This code implements the algorithm presented in the ICML 2003
% paper "Using the Triangle Inequality to Accelerate K-Means" from
% Charles Elkan
%
% builds up on a previous version using the standard algorithm from
% Mark Everingham <me@robots.ox.ac.uk>
%
% Author: Peter Gehler <pgehler@tuebingen.mpg.de>
% Date: 12 Dec 07


if ~exist('nr_restarts','var')
    nr_restarts = 0;
end

if ~exist('maxiterations','var') || numel(maxiterations) == 0
  maxiterations = 0;
end
if isinf(maxiterations), maxiterations = 0; end

if nr_restarts > 0
    minsse = Inf;
    for i=1:nr_restarts+1
	nclus = initcenters;
	perm=randperm(size(X,2));
	CX=X(:,perm(1:nclus));
	[tCx,sse,assign] = mpi_kmeans(X,CX,maxiterations,0);
	if sse<minsse
	    minsse = sse;
	    Cx = tCx;
	    assignment = assign;
	end 
    end	    
    sse = minsse;
else

    if max(size(initcenters))==1
	nclus = initcenters;
	if nclus > size(X,2)
	    error('more clusters requested as training points available');
	end
	perm=randperm(size(X,2));
	CX=X(:,perm(1:nclus));
    else
	CX = initcenters;
	nclus = size(CX,2);
	if size(CX,1) ~= size(X,1)
	    error('dimension mismatch of centers and datapoints');
	end
    end


    if nargout > 3
	error('number of output arguments at most 2');
    elseif nargout == 2
	[CX,sse] = mpi_kmeans_mex(X, CX,maxiterations);    
    elseif nargout == 3
	[CX,sse,assignment] = mpi_kmeans_mex(X, CX,maxiterations);    
    else % this saves a bit as the correct sse must not be calculated
	CX = mpi_kmeans_mex(X, CX,maxiterations);    
    end
end



